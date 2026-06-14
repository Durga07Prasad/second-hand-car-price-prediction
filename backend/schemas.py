"""
Pydantic schemas for request validation and response serialization.
FastAPI uses these to auto-generate Swagger docs and validate input/output.
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

from config import (
    VALID_BRANDS, VALID_FUELS, VALID_SELLER_TYPES,
    VALID_TRANSMISSIONS, VALID_OWNERS, CURRENT_YEAR,
)


# ─── Request Schemas ──────────────────────────────────────────────────

class CarInput(BaseModel):
    """
    Raw car details as a user would enter them.
    The API handles all preprocessing (encoding, scaling, feature engineering).
    """
    brand: str = Field(
        ...,
        description="Car brand name",
        examples=["Maruti"],
    )
    year: int = Field(
        ...,
        ge=1990,
        le=CURRENT_YEAR,
        description="Year of manufacture",
        examples=[2015],
    )
    km_driven: int = Field(
        ...,
        ge=0,
        description="Total kilometers driven",
        examples=[50000],
    )
    fuel: str = Field(
        ...,
        description="Fuel type",
        examples=["Petrol"],
    )
    seller_type: str = Field(
        ...,
        description="Type of seller",
        examples=["Individual"],
    )
    transmission: str = Field(
        ...,
        description="Transmission type",
        examples=["Manual"],
    )
    owner: str = Field(
        ...,
        description="Ownership history",
        examples=["First Owner"],
    )

    @field_validator("brand")
    @classmethod
    def validate_brand(cls, v: str) -> str:
        if v not in VALID_BRANDS:
            raise ValueError(
                f"Unknown brand '{v}'. Must be one of: {', '.join(VALID_BRANDS)}"
            )
        return v

    @field_validator("fuel")
    @classmethod
    def validate_fuel(cls, v: str) -> str:
        if v not in VALID_FUELS:
            raise ValueError(
                f"Invalid fuel type '{v}'. Must be one of: {', '.join(VALID_FUELS)}"
            )
        return v

    @field_validator("seller_type")
    @classmethod
    def validate_seller_type(cls, v: str) -> str:
        if v not in VALID_SELLER_TYPES:
            raise ValueError(
                f"Invalid seller type '{v}'. Must be one of: {', '.join(VALID_SELLER_TYPES)}"
            )
        return v

    @field_validator("transmission")
    @classmethod
    def validate_transmission(cls, v: str) -> str:
        if v not in VALID_TRANSMISSIONS:
            raise ValueError(
                f"Invalid transmission '{v}'. Must be one of: {', '.join(VALID_TRANSMISSIONS)}"
            )
        return v

    @field_validator("owner")
    @classmethod
    def validate_owner(cls, v: str) -> str:
        if v not in VALID_OWNERS:
            raise ValueError(
                f"Invalid owner type '{v}'. Must be one of: {', '.join(VALID_OWNERS)}"
            )
        return v


# ─── Response Schemas ─────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    """Response for the /predict endpoint."""
    predicted_price: float = Field(..., description="Predicted selling price in INR")
    currency: str = Field(default="INR", description="Currency code")
    model_used: str = Field(..., description="Name of the ML model used")
    model_r2_score: float = Field(..., description="Model R² score on test set")


class SHAPFactor(BaseModel):
    """A single SHAP factor explaining a prediction."""
    feature: str = Field(..., description="Human-readable feature name")
    shap_value: float = Field(..., description="SHAP contribution in INR")
    impact: str = Field(..., description="'increases' or 'decreases' the price")


class ExplanationResponse(BaseModel):
    """Response for the /predict-with-explanation endpoint."""
    predicted_price: float = Field(..., description="Predicted selling price in INR")
    currency: str = Field(default="INR", description="Currency code")
    model_used: str = Field(..., description="Name of the ML model used")
    model_r2_score: float = Field(..., description="Model R² score on test set")
    base_value: float = Field(..., description="Average predicted price (SHAP base)")
    top_factors: List[SHAPFactor] = Field(..., description="Top SHAP factors")
    explanation_text: str = Field(..., description="Human-readable explanation")


class FeatureImportanceItem(BaseModel):
    """A single feature with its importance score."""
    rank: int
    feature: str = Field(..., description="Human-readable feature name")
    technical_name: str = Field(..., description="Internal feature column name")
    importance: float = Field(..., description="CatBoost feature importance score")


class ModelInfoResponse(BaseModel):
    """Response for the /model-info endpoint."""
    model_name: str
    r2_score: float
    rmse: float
    mae: float
    cv_r2_mean: float
    training_date: str
    feature_count: int
    features_used: List[str]


class HealthResponse(BaseModel):
    """Response for the /health endpoint."""
    status: str = Field(default="healthy")
    model_loaded: bool = Field(..., description="Whether the model loaded successfully")
    version: str


# ─── Database & Feedback Schemas ──────────────────────────────────────

from datetime import datetime
from typing import Dict, Any

class PredictionHistoryItem(BaseModel):
    id: int
    brand: str
    year: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    predicted_price: float
    model_used: str
    device_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PredictionHistoryResponse(BaseModel):
    total: int
    predictions: List[PredictionHistoryItem]

class PredictionStatsResponse(BaseModel):
    total_predictions: int
    avg_predicted_price: Optional[float]
    most_common_brand: Optional[str]
    predictions_today: int
    device_breakdown: Dict[str, int]

class FeedbackInput(BaseModel):
    prediction_id: int
    actual_price: Optional[float] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    id: int
