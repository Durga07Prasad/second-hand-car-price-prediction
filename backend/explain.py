"""
SHAP-based explainability for individual predictions.

Provides human-readable explanations of WHY the model predicted a
specific price, using SHAP values or CatBoost feature importances
as a fallback.
"""
import logging

import numpy as np
import pandas as pd

from model_loader import ModelLoader

logger = logging.getLogger(__name__)

# ─── Human-Readable Feature Labels ────────────────────────────────────
FEATURE_LABELS = {
    "km_driven":                      "Total Kilometers Driven",
    "brand":                          "Car Brand",
    "car_age":                        "Vehicle Age",
    "km_per_year":                    "Annual Usage Rate",
    "fuel_Diesel":                    "Diesel Fuel Type",
    "fuel_Electric":                  "Electric Vehicle",
    "fuel_LPG":                       "LPG Fuel Type",
    "fuel_Petrol":                    "Petrol Fuel Type",
    "seller_type_Individual":         "Individual Seller",
    "seller_type_Trustmark Dealer":   "Trustmark Certified Dealer",
    "transmission_Manual":            "Manual Transmission",
    "owner_Fourth & Above Owner":     "Fourth or More Owners",
    "owner_Second Owner":             "Second Owner",
    "owner_Test Drive Car":           "Test Drive Vehicle",
    "owner_Third Owner":              "Third Owner",
    "brand_tier_Luxury":              "Luxury Brand Segment",
    "brand_tier_Mid-range":           "Mid-Range Brand Segment",
    "brand_tier_Premium":             "Premium Brand Segment",
}


def _human_label(feature_name: str) -> str:
    """Map technical feature name to a human-readable label."""
    return FEATURE_LABELS.get(feature_name, feature_name)


# ─── SHAP Explanation ─────────────────────────────────────────────────

def explain_prediction(
    input_df: pd.DataFrame,
    loader: ModelLoader,
    top_n: int = 5,
) -> dict:
    """
    Explain a single prediction using SHAP values.

    Falls back to CatBoost's built-in feature_importances_ if the SHAP
    explainer is unavailable.

    Args:
        input_df:  Preprocessed single-row DataFrame (18 columns, model-ready).
        loader:    ModelLoader instance with all artifacts.
        top_n:     Number of top factors to return.

    Returns:
        dict with keys:
            base_value      – Average predicted price (SHAP expected value)
            predicted_price – Model prediction for this car
            top_factors     – List of {feature, shap_value, impact} dicts
    """
    model = loader.get_model()
    explainer = loader.get_shap_explainer()
    feature_names = loader.get_feature_columns()
    predicted_price = float(model.predict(input_df)[0])

    if explainer is not None:
        # ── SHAP path ────────────────────────────────────────────
        try:
            shap_values = explainer.shap_values(input_df)
            # Handle both 1-D and 2-D return shapes
            if len(shap_values.shape) == 1:
                sv = shap_values
            else:
                sv = shap_values[0]

            raw_base = explainer.expected_value
            base_value = float(np.atleast_1d(raw_base).flatten()[0])

            factors = []
            for i, fname in enumerate(feature_names):
                val = float(sv[i])
                factors.append({
                    "feature": _human_label(fname),
                    "shap_value": round(val, 2),
                    "impact": "increases" if val > 0 else "decreases",
                })

            # Sort by absolute SHAP value descending, keep top_n
            factors.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
            factors = factors[:top_n]

            logger.info("SHAP explanation generated (%d factors)", len(factors))
            return {
                "base_value": round(base_value, 2),
                "predicted_price": round(predicted_price, 2),
                "top_factors": factors,
            }

        except Exception as exc:
            logger.warning("SHAP failed (%s), falling back to feature_importances_", exc)

    # ── Fallback: CatBoost feature_importances_ ──────────────────
    logger.info("Using feature_importances_ fallback for explanation")
    importances = model.feature_importances_
    base_value = predicted_price  # no true base when using importances

    factors = []
    for i, fname in enumerate(feature_names):
        factors.append({
            "feature": _human_label(fname),
            "shap_value": round(float(importances[i]), 2),
            "impact": "influences",
        })
    factors.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    factors = factors[:top_n]

    return {
        "base_value": round(base_value, 2),
        "predicted_price": round(predicted_price, 2),
        "top_factors": factors,
    }


# ─── Human-Readable Text ─────────────────────────────────────────────

def generate_explanation_text(
    base_value: float,
    predicted_price: float,
    top_factors: list,
) -> str:
    """
    Generate a natural-language paragraph explaining the prediction.

    Example output:
        "This car is predicted at Rs.4,50,000. Starting from an average
        price of Rs.4,62,000, the following factors adjusted the price:
        Vehicle Age: +Rs.2,10,000 (increases price), ..."
    """
    lines = [
        f"This car is predicted at Rs.{predicted_price:,.0f}.",
        f"Starting from an average price of Rs.{base_value:,.0f}, "
        f"the following factors adjusted the price:",
    ]

    for factor in top_factors:
        label = factor["feature"]
        val = factor["shap_value"]
        impact = factor["impact"]
        sign = "+" if val > 0 else "-"
        lines.append(
            f"  {label}: {sign}Rs.{abs(val):,.0f} ({impact} price)"
        )

    return "\n".join(lines)
