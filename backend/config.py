"""
Configuration settings for the Car Price Prediction API.
Centralizes all app-wide constants, paths, and mappings.
"""
import os

# ─── Application Settings ────────────────────────────────────────────
APP_NAME = "Car Price Prediction API"
APP_DESCRIPTION = (
    "Production-ready API for predicting second-hand car prices in India. "
    "Powered by a CatBoost model trained on CarDekho data with R²=0.80. "
    "Includes SHAP-based explainability for transparent predictions."
)
APP_VERSION = "1.0.0"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./car_predictions.db")

# ─── Paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "app_models")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# ─── Model Reference Year ────────────────────────────────────────────
# The preprocessing notebook used 2024 as the reference year for car_age.
# Change this only if you retrain with a different reference.
CURRENT_YEAR = 2024

# ─── Brand Tier Mapping ──────────────────────────────────────────────
# Derived from the preprocessing notebook's logic:
#   Luxury: avg_price > ₹15,00,000
#   Premium: ₹7,00,000 – ₹15,00,000
#   Mid-range: ₹3,50,000 – ₹7,00,000
#   Budget: < ₹3,50,000
# These tiers were computed from the training data (cleaned_car_data.csv groupby brand).
BRAND_TIER_MAP = {
    "Audi": "Luxury",
    "BMW": "Luxury",
    "Mercedes-Benz": "Luxury",
    "Chevrolet": "Budget",
    "Fiat": "Budget",
    "Ford": "Mid-range",
    "Honda": "Mid-range",
    "Hyundai": "Mid-range",
    "Mahindra": "Mid-range",
    "Maruti": "Budget",
    "Nissan": "Budget",
    "Renault": "Budget",
    "Skoda": "Premium",
    "Tata": "Budget",
    "Toyota": "Premium",
    "Volkswagen": "Mid-range",
    "Other": "Mid-range",
}

# ─── Valid Categories ─────────────────────────────────────────────────
# Used for validation in schemas.py
VALID_BRANDS = [
    "Audi", "Chevrolet", "Fiat", "Ford", "Honda", "Hyundai",
    "Mahindra", "Maruti", "Nissan", "Other", "Renault", "Skoda",
    "Tata", "Toyota", "Volkswagen",
]

VALID_FUELS = ["Petrol", "Diesel", "CNG", "LPG", "Electric"]
VALID_SELLER_TYPES = ["Individual", "Dealer", "Trustmark Dealer"]
VALID_TRANSMISSIONS = ["Manual", "Automatic"]
VALID_OWNERS = [
    "First Owner", "Second Owner", "Third Owner",
    "Fourth & Above Owner", "Test Drive Car",
]
