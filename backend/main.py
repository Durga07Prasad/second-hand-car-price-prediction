"""
Car Price Prediction API — FastAPI Application

Endpoints:
    GET  /                          Welcome message
    GET  /health                    Health check
    GET  /model-info                Model metadata
    GET  /feature-importance        Top 15 features by importance
    POST /predict                   Predict car price
    POST /predict-with-explanation  Predict with SHAP explanation
    GET  /predictions/history       Recent predictions
    GET  /predictions/stats         Prediction statistics
    POST /feedback                  Submit user feedback

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""
import logging
import sys
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from config import APP_NAME, APP_DESCRIPTION, APP_VERSION, LOG_FILE
from schemas import (
    CarInput,
    PredictionResponse,
    ExplanationResponse,
    SHAPFactor,
    FeatureImportanceItem,
    ModelInfoResponse,
    HealthResponse,
    PredictionHistoryResponse,
    PredictionHistoryItem,
    PredictionStatsResponse,
    FeedbackInput,
    FeedbackResponse,
)
from model_loader import ModelLoader
from predictor import predict_price, preprocess_input
from explain import (
    explain_prediction,
    generate_explanation_text,
    FEATURE_LABELS,
)
from database import engine, get_db, Base
from db_models import Prediction, Feedback

# ─── Logging Setup ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("app")

# ─── Global Model Loader ─────────────────────────────────────────────

loader: ModelLoader = None  # initialized in lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all model artifacts once at startup."""
    global loader
    logger.info("Starting %s v%s ...", APP_NAME, APP_VERSION)
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created.")
    except Exception as exc:
        logger.error("Failed to initialize database tables: %s", exc)
        
    try:
        loader = ModelLoader()
        logger.info("Model loader initialized successfully.")
    except Exception as exc:
        logger.critical("Failed to load model artifacts: %s", exc, exc_info=True)
        raise
    yield
    logger.info("Shutting down %s.", APP_NAME)


# ─── FastAPI App ──────────────────────────────────────────────────────

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

# CORS — allow all origins for development.
# In production, restrict to your frontend domain(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════


@app.get("/", tags=["General"])
def root():
    """Welcome message with API info and links."""
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """Check if the API and model are operational."""
    return HealthResponse(
        status="healthy" if loader and loader.is_model_loaded() else "unhealthy",
        model_loaded=loader.is_model_loaded() if loader else False,
        version=APP_VERSION,
    )


@app.get("/model-info", response_model=ModelInfoResponse, tags=["Model"])
def model_info():
    """
    Return metadata about the trained model — name, metrics, features,
    and training date. Useful for dashboards and monitoring.
    """
    meta = loader.get_metadata()
    return ModelInfoResponse(
        model_name=meta["best_model_name"],
        r2_score=meta["r2"],
        rmse=meta["rmse"],
        mae=meta["mae"],
        cv_r2_mean=meta["cv_r2_mean"],
        training_date=meta["training_date"],
        feature_count=len(meta["feature_columns"]),
        features_used=meta["feature_columns"],
    )


@app.get(
    "/feature-importance",
    response_model=list[FeatureImportanceItem],
    tags=["Model"],
)
def feature_importance():
    """
    Return top 15 features ranked by CatBoost's built-in feature
    importance scores, with human-readable labels.
    """
    model = loader.get_model()
    feature_cols = loader.get_feature_columns()
    importances = model.feature_importances_

    # Pair and sort descending
    paired = sorted(
        zip(feature_cols, importances),
        key=lambda x: x[1],
        reverse=True,
    )[:15]

    return [
        FeatureImportanceItem(
            rank=i + 1,
            feature=FEATURE_LABELS.get(name, name),
            technical_name=name,
            importance=round(float(score), 4),
        )
        for i, (name, score) in enumerate(paired)
    ]


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(
    car: CarInput,
    x_device_type: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Predict the selling price of a second-hand car.

    Send raw car details (brand, year, km, fuel, etc.) and receive a
    predicted price in INR along with model confidence metrics.
    """
    try:
        price = predict_price(car, loader)
        meta = loader.get_metadata()
        
        # Save to DB asynchronously (or within the request since it's fast enough)
        try:
            db_prediction = Prediction(
                brand=car.brand, year=car.year, km_driven=car.km_driven,
                fuel=car.fuel, seller_type=car.seller_type,
                transmission=car.transmission, owner=car.owner,
                predicted_price=price, model_used=meta["best_model_name"],
                model_r2_score=round(meta["r2"], 4),
                device_type=x_device_type or "unknown"
            )
            db.add(db_prediction)
            db.commit()
        except Exception as db_exc:
            logger.error("Database save failed: %s", db_exc)
            
        return PredictionResponse(
            predicted_price=price,
            currency="INR",
            model_used=meta["best_model_name"],
            model_r2_score=round(meta["r2"], 4),
        )
    except Exception as exc:
        logger.error("Prediction failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}")


@app.post(
    "/predict-with-explanation",
    response_model=ExplanationResponse,
    tags=["Prediction"],
)
def predict_with_explanation(
    car: CarInput,
    x_device_type: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Predict car price **and** explain WHY using SHAP values.

    Returns the predicted price, the average (base) price, the top 5
    contributing factors, and a human-readable explanation paragraph.
    """
    try:
        # Preprocess once, reuse for both prediction and explanation
        input_df = preprocess_input(car, loader)
        price = float(loader.get_model().predict(input_df)[0])
        price = round(price / 100) * 100
        price = max(price, 0)

        # SHAP explanation
        explanation = explain_prediction(input_df, loader, top_n=5)
        text = generate_explanation_text(
            explanation["base_value"],
            price,
            explanation["top_factors"],
        )

        meta = loader.get_metadata()
        
        # Save to DB
        try:
            db_prediction = Prediction(
                brand=car.brand, year=car.year, km_driven=car.km_driven,
                fuel=car.fuel, seller_type=car.seller_type,
                transmission=car.transmission, owner=car.owner,
                predicted_price=price, model_used=meta["best_model_name"],
                model_r2_score=round(meta["r2"], 4),
                device_type=x_device_type or "unknown"
            )
            db.add(db_prediction)
            db.commit()
        except Exception as db_exc:
            logger.error("Database save failed: %s", db_exc)

        return ExplanationResponse(
            predicted_price=price,
            currency="INR",
            model_used=meta["best_model_name"],
            model_r2_score=round(meta["r2"], 4),
            base_value=explanation["base_value"],
            top_factors=[SHAPFactor(**f) for f in explanation["top_factors"]],
            explanation_text=text,
        )
    except Exception as exc:
        logger.error("Explanation failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Explanation error: {exc}")


# ─── Database Analytics & Feedback Endpoints ─────────────────────────

@app.get("/predictions/history", response_model=PredictionHistoryResponse, tags=["Analytics"])
def get_prediction_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Fetch recent predictions from the database."""
    total = db.query(Prediction).count()
    predictions = db.query(Prediction).order_by(desc(Prediction.created_at)).offset(offset).limit(limit).all()
    
    return PredictionHistoryResponse(
        total=total,
        predictions=[PredictionHistoryItem.model_validate(p) for p in predictions]
    )


@app.get("/predictions/stats", response_model=PredictionStatsResponse, tags=["Analytics"])
def get_prediction_stats(db: Session = Depends(get_db)):
    """Fetch aggregated prediction statistics."""
    total_predictions = db.query(Prediction).count()
    
    if total_predictions == 0:
        return PredictionStatsResponse(
            total_predictions=0,
            avg_predicted_price=None,
            most_common_brand=None,
            predictions_today=0,
            device_breakdown={"unknown": 0}
        )
        
    avg_price = db.query(func.avg(Prediction.predicted_price)).scalar()
    
    brand_counts = db.query(Prediction.brand, func.count(Prediction.id)).group_by(Prediction.brand).order_by(desc(func.count(Prediction.id))).first()
    most_common_brand = brand_counts[0] if brand_counts else None
    
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    predictions_today = db.query(Prediction).filter(Prediction.created_at >= today).count()
    
    device_counts = db.query(Prediction.device_type, func.count(Prediction.id)).group_by(Prediction.device_type).all()
    device_breakdown = {d_type or "unknown": count for d_type, count in device_counts}
    
    return PredictionStatsResponse(
        total_predictions=total_predictions,
        avg_predicted_price=avg_price,
        most_common_brand=most_common_brand,
        predictions_today=predictions_today,
        device_breakdown=device_breakdown
    )


@app.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
def submit_feedback(feedback: FeedbackInput, db: Session = Depends(get_db)):
    """Submit user feedback for a specific prediction."""
    prediction = db.query(Prediction).filter(Prediction.id == feedback.prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction ID not found")
        
    new_feedback = Feedback(
        prediction_id=feedback.prediction_id,
        actual_price=feedback.actual_price,
        rating=feedback.rating,
        comment=feedback.comment
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    return FeedbackResponse(status="success", id=new_feedback.id)
