"""
Preprocessing pipeline and prediction logic.

Converts raw CarInput (human-readable fields) into the exact 18-column
DataFrame the model expects, then runs inference.
"""
import logging

import numpy as np
import pandas as pd

from config import CURRENT_YEAR, BRAND_TIER_MAP
from schemas import CarInput
from model_loader import ModelLoader

logger = logging.getLogger(__name__)


# ─── Preprocessing ────────────────────────────────────────────────────

def preprocess_input(car_input: CarInput, loader: ModelLoader) -> pd.DataFrame:
    """
    Transform raw user input into a model-ready single-row DataFrame.

    Steps:
        1. Feature engineering (car_age, km_per_year, brand_tier)
        2. Label-encode brand
        3. One-hot encode categoricals (matching training-time columns)
        4. Scale numerical features
        5. Assemble in exact feature_columns order

    Returns:
        pd.DataFrame with shape (1, 18) and columns in model's expected order.
    """
    feature_columns = loader.get_feature_columns()
    scaler = loader.get_scaler()
    brand_encoder = loader.get_brand_encoder()

    # ── 1. Feature engineering ────────────────────────────────────────
    car_age = CURRENT_YEAR - car_input.year
    km_per_year = car_input.km_driven / (car_age + 1)

    # Determine brand tier
    brand_tier = BRAND_TIER_MAP.get(car_input.brand, "Mid-range")

    # ── 2. Label-encode brand ─────────────────────────────────────────
    # If the brand is unknown to the encoder, fall back to "Other"
    brand_str = car_input.brand
    known_brands = list(brand_encoder.classes_)
    if brand_str not in known_brands:
        logger.warning("Unknown brand '%s' — mapping to 'Other'", brand_str)
        brand_str = "Other"
    brand_encoded = int(brand_encoder.transform([brand_str])[0])

    # ── 3. One-hot encode categoricals ────────────────────────────────
    # Reference (dropped) categories:
    #   fuel=CNG, seller_type=Dealer, transmission=Automatic,
    #   owner=First Owner, brand_tier=Budget
    # We only create columns for the non-reference categories.

    fuel = car_input.fuel
    seller_type = car_input.seller_type
    transmission = car_input.transmission
    owner = car_input.owner

    one_hot = {
        # fuel (reference: CNG)
        "fuel_Diesel":    1 if fuel == "Diesel" else 0,
        "fuel_Electric":  1 if fuel == "Electric" else 0,
        "fuel_LPG":       1 if fuel == "LPG" else 0,
        "fuel_Petrol":    1 if fuel == "Petrol" else 0,
        # seller_type (reference: Dealer)
        "seller_type_Individual":       1 if seller_type == "Individual" else 0,
        "seller_type_Trustmark Dealer": 1 if seller_type == "Trustmark Dealer" else 0,
        # transmission (reference: Automatic)
        "transmission_Manual": 1 if transmission == "Manual" else 0,
        # owner (reference: First Owner)
        "owner_Fourth & Above Owner": 1 if owner == "Fourth & Above Owner" else 0,
        "owner_Second Owner":         1 if owner == "Second Owner" else 0,
        "owner_Test Drive Car":       1 if owner == "Test Drive Car" else 0,
        "owner_Third Owner":          1 if owner == "Third Owner" else 0,
        # brand_tier (reference: Budget)
        "brand_tier_Luxury":    1 if brand_tier == "Luxury" else 0,
        "brand_tier_Mid-range": 1 if brand_tier == "Mid-range" else 0,
        "brand_tier_Premium":   1 if brand_tier == "Premium" else 0,
    }

    # ── 4. Scale numerical features ───────────────────────────────────
    # Scaler was fitted on [km_driven, car_age, km_per_year] (3 columns)
    numericals_raw = pd.DataFrame(
        [[car_input.km_driven, car_age, km_per_year]],
        columns=["km_driven", "car_age", "km_per_year"],
    )
    numericals_scaled = scaler.transform(numericals_raw)
    km_driven_scaled = numericals_scaled[0][0]
    car_age_scaled = numericals_scaled[0][1]
    km_per_year_scaled = numericals_scaled[0][2]

    # ── 5. Assemble in exact feature_columns order ────────────────────
    row_data = {
        "km_driven":  km_driven_scaled,
        "brand":      brand_encoded,
        "car_age":    car_age_scaled,
        "km_per_year": km_per_year_scaled,
    }
    row_data.update(one_hot)

    # Build DataFrame in the exact column order the model expects
    result = pd.DataFrame([row_data], columns=feature_columns)

    logger.debug(
        "Preprocessed input: brand=%s(enc=%d), car_age=%d, tier=%s -> %s",
        car_input.brand, brand_encoded, car_age, brand_tier,
        result.values.tolist(),
    )
    return result


# ─── Prediction ───────────────────────────────────────────────────────

def predict_price(car_input: CarInput, loader: ModelLoader) -> float:
    """
    End-to-end prediction: preprocess raw input → model.predict → price.

    Returns:
        float: Predicted selling price in INR, rounded to nearest ₹100.
    """
    input_df = preprocess_input(car_input, loader)
    raw_prediction = loader.get_model().predict(input_df)[0]

    # Round to nearest 100 for cleaner output
    predicted_price = round(float(raw_prediction) / 100) * 100
    predicted_price = max(predicted_price, 0)  # price can't be negative

    logger.info(
        "Prediction: %s %d (%dkm, %s, %s) -> Rs.%s",
        car_input.brand, car_input.year, car_input.km_driven,
        car_input.fuel, car_input.transmission,
        f"{predicted_price:,.0f}",
    )
    return float(predicted_price)
