# 🚗 Car Price Prediction API

Production-ready FastAPI backend for predicting second-hand car prices in India.  
Powered by a **CatBoost** model (R² = 0.80, RMSE = ₹1,83,597) with **SHAP explainability**.

---

## Quick Start

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the server
```bash
uvicorn main:app --reload --port 8000
```

### 3. Open Swagger Docs
Visit: **http://localhost:8000/docs**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Welcome message |
| `GET`  | `/health` | Health check |
| `GET`  | `/model-info` | Model metadata & metrics |
| `GET`  | `/feature-importance` | Top 15 features ranked |
| `POST` | `/predict` | Predict car price |
| `POST` | `/predict-with-explanation` | Predict + SHAP explanation |

---

## Example: Predict Price

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d "{\"brand\": \"Maruti\", \"year\": 2015, \"km_driven\": 50000, \"fuel\": \"Petrol\", \"seller_type\": \"Individual\", \"transmission\": \"Manual\", \"owner\": \"First Owner\"}"
```

**Response:**
```json
{
  "predicted_price": 345000.0,
  "currency": "INR",
  "model_used": "CatBoost",
  "model_r2_score": 0.8013
}
```

---

## Example: Predict with Explanation

```bash
curl -X POST http://localhost:8000/predict-with-explanation \
  -H "Content-Type: application/json" \
  -d "{\"brand\": \"Maruti\", \"year\": 2015, \"km_driven\": 50000, \"fuel\": \"Petrol\", \"seller_type\": \"Individual\", \"transmission\": \"Manual\", \"owner\": \"First Owner\"}"
```

**Response:**
```json
{
  "predicted_price": 345000.0,
  "currency": "INR",
  "model_used": "CatBoost",
  "model_r2_score": 0.8013,
  "base_value": 461754.71,
  "top_factors": [
    {"feature": "Vehicle Age", "shap_value": -85000.0, "impact": "decreases"},
    {"feature": "Manual Transmission", "shap_value": -30000.0, "impact": "decreases"}
  ],
  "explanation_text": "This car is predicted at ₹3,45,000..."
}
```

---

## Valid Input Values

| Field | Valid Values |
|-------|-------------|
| `brand` | Audi, Chevrolet, Fiat, Ford, Honda, Hyundai, Mahindra, Maruti, Nissan, Other, Renault, Skoda, Tata, Toyota, Volkswagen |
| `year` | 1990 – 2024 |
| `km_driven` | ≥ 0 |
| `fuel` | Petrol, Diesel, CNG, LPG, Electric |
| `seller_type` | Individual, Dealer, Trustmark Dealer |
| `transmission` | Manual, Automatic |
| `owner` | First Owner, Second Owner, Third Owner, Fourth & Above Owner, Test Drive Car |

---

## Project Structure

```
backend/
├── main.py              # FastAPI app with all endpoints
├── config.py            # Settings, paths, brand tier mapping
├── schemas.py           # Pydantic request/response models
├── model_loader.py      # Singleton model artifact loader
├── predictor.py         # Preprocessing + prediction logic
├── explain.py           # SHAP explanation functions
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── app_models/          # Serialized ML artifacts
│   ├── best_model.pkl
│   ├── scaler.pkl
│   ├── brand_encoder.pkl
│   ├── feature_columns.pkl
│   ├── model_metadata.json
│   └── shap_explainer.pkl
└── logs/
    └── app.log          # Runtime logs
```
