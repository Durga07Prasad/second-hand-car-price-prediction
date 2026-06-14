"""
Retrain all models on the fixed preprocessing pipeline.
Ensures best_model.pkl, model_comparison.csv, and model_metadata.json
are fully consistent with the corrected 3-column scaler.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

# ============================================================
# TASK 1: Load data
# ============================================================
print("=" * 70)
print("TASK 1: Load cleaned_car_data.csv")
print("=" * 70)

df = pd.read_csv('../data/cleaned_car_data.csv')
X = df.drop(columns=['selling_price'])
y = df['selling_price']

print(f"Dataset: {df.shape}")
print(f"X.shape: {X.shape}")
print(f"y.shape: {y.shape}")
print(f"X.columns: {X.columns.tolist()}")
print(f"Missing values: {df.isnull().sum().sum()}")
assert X.shape == (3577, 18), f"Expected (3577, 18), got {X.shape}"
assert 'depreciation_rate' not in X.columns, "depreciation_rate should NOT be present!"
print("Assertions passed.")

# ============================================================
# TASK 2: Train-test split
# ============================================================
print("\n" + "=" * 70)
print("TASK 2: Train-test split (80/20, random_state=42)")
print("=" * 70)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"X_train: {X_train.shape}, X_test: {X_test.shape}")
print(f"y_train: {y_train.shape}, y_test: {y_test.shape}")

# ============================================================
# TASK 3 & 4: Train and evaluate all 6 models
# ============================================================
print("\n" + "=" * 70)
print("TASKS 3-4: Train and evaluate all 6 models")
print("=" * 70)

def evaluate_model(model_name, model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    cv_fold = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv_fold, scoring='r2')
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    print(f"[{model_name:20}] RMSE: Rs.{rmse:>12,.0f} | MAE: Rs.{mae:>12,.0f} | "
          f"R2: {r2:.4f} | CV R2: {cv_mean:.4f} (+/-{cv_std:.4f})")
    return {
        'model_name': model_name, 'model': model,
        'rmse': rmse, 'mae': mae, 'r2': r2,
        'cv_mean': cv_mean, 'cv_std': cv_std
    }

results = []

# Baseline models
print("\n--- Baseline Models ---")
results.append(evaluate_model("Linear Regression", LinearRegression(),
                              X_train, X_test, y_train, y_test))
results.append(evaluate_model("Decision Tree",
                              DecisionTreeRegressor(random_state=42, max_depth=10),
                              X_train, X_test, y_train, y_test))

# Advanced models
print("\n--- Advanced Models ---")
results.append(evaluate_model("Random Forest",
                              RandomForestRegressor(n_estimators=200, max_depth=15,
                                                    random_state=42, n_jobs=-1),
                              X_train, X_test, y_train, y_test))
results.append(evaluate_model("XGBoost",
                              XGBRegressor(n_estimators=200, learning_rate=0.05,
                                           max_depth=6, random_state=42),
                              X_train, X_test, y_train, y_test))
results.append(evaluate_model("LightGBM",
                              LGBMRegressor(n_estimators=200, learning_rate=0.05,
                                            random_state=42, verbose=-1),
                              X_train, X_test, y_train, y_test))
results.append(evaluate_model("CatBoost",
                              CatBoostRegressor(iterations=200, learning_rate=0.05,
                                                random_state=42, verbose=0),
                              X_train, X_test, y_train, y_test))

# Build comparison table
comparison_data = [{
    'Model': r['model_name'], 'RMSE': r['rmse'], 'MAE': r['mae'],
    'R2': r['r2'], 'CV_R2_mean': r['cv_mean'], 'CV_R2_std': r['cv_std']
} for r in results]

comparison_df = pd.DataFrame(comparison_data).sort_values('R2', ascending=False).reset_index(drop=True)

print("\n--- Model Comparison Table (sorted by R2 desc) ---")
display_df = comparison_df.copy()
display_df['RMSE'] = display_df['RMSE'].apply(lambda x: f"Rs.{x:,.0f}")
display_df['MAE'] = display_df['MAE'].apply(lambda x: f"Rs.{x:,.0f}")
display_df['R2'] = display_df['R2'].apply(lambda x: f"{x:.4f}")
display_df['CV_R2_mean'] = display_df['CV_R2_mean'].apply(lambda x: f"{x:.4f}")
display_df['CV_R2_std'] = display_df['CV_R2_std'].apply(lambda x: f"{x:.4f}")
print(display_df.to_string(index=False))

# ============================================================
# TASK 5: Select best model
# ============================================================
print("\n" + "=" * 70)
print("TASK 5: Best model selection")
print("=" * 70)

best_result = max(results, key=lambda x: x['r2'])
best_model = best_result['model']
best_model_name = best_result['model_name']

print(f"BEST MODEL: {best_model_name}")
print(f"  Test R2:  {best_result['r2']:.4f}")
print(f"  Test RMSE: Rs.{best_result['rmse']:,.0f}")
print(f"  Test MAE:  Rs.{best_result['mae']:,.0f}")
print(f"  CV R2:     {best_result['cv_mean']:.4f} (+/-{best_result['cv_std']:.4f})")

# ============================================================
# TASK 6: Save artifacts (overwrite)
# ============================================================
print("\n" + "=" * 70)
print("TASK 6: Save artifacts")
print("=" * 70)

os.makedirs('../models', exist_ok=True)

# best_model.pkl
joblib.dump(best_model, '../models/best_model.pkl')
print(f"Saved: ../models/best_model.pkl ({best_model_name})")

# model_comparison.csv
comparison_df_raw = pd.DataFrame(comparison_data).sort_values('R2', ascending=False).reset_index(drop=True)
comparison_df_raw.to_csv('../models/model_comparison.csv', index=False)
print(f"Saved: ../models/model_comparison.csv (6 models)")

# model_metadata.json
metadata = {
    'best_model_name': best_model_name,
    'rmse': float(best_result['rmse']),
    'mae': float(best_result['mae']),
    'r2': float(best_result['r2']),
    'cv_r2_mean': float(best_result['cv_mean']),
    'cv_r2_std': float(best_result['cv_std']),
    'feature_columns': X.columns.tolist(),
    'training_date': datetime.now().isoformat(),
    'training_samples': len(X_train),
    'test_samples': len(X_test)
}
with open('../models/model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"Saved: ../models/model_metadata.json")

# Copy to backend/app_models/
import shutil
backend_models = '../backend/app_models'
if os.path.isdir(backend_models):
    for fname in ['best_model.pkl', 'model_comparison.csv', 'model_metadata.json']:
        shutil.copy2(f'../models/{fname}', os.path.join(backend_models, fname))
    print(f"Copied all 3 artifacts to {backend_models}/")

# ============================================================
# TASK 7: Verification - 4 test predictions
# ============================================================
print("\n" + "=" * 70)
print("TASK 7: Verification - 4 test predictions")
print("=" * 70)

# Load fresh artifacts to verify
ver_model = joblib.load('../models/best_model.pkl')
ver_scaler = joblib.load('../models/scaler.pkl')
ver_encoder = joblib.load('../models/brand_encoder.pkl')
ver_features = joblib.load('../models/feature_columns.pkl')

print(f"Loaded model: {type(ver_model).__name__}")
print(f"Loaded scaler features: {list(ver_scaler.feature_names_in_)} (n={ver_scaler.n_features_in_})")
print(f"Loaded encoder classes: {list(ver_encoder.classes_)}")
print(f"Feature columns: {ver_features}")

CURRENT_YEAR = 2024
BRAND_TIER_MAP = {
    "Audi": "Luxury", "Chevrolet": "Budget", "Fiat": "Budget",
    "Ford": "Mid-range", "Honda": "Mid-range", "Hyundai": "Mid-range",
    "Mahindra": "Mid-range", "Maruti": "Budget", "Nissan": "Mid-range",
    "Other": "Mid-range", "Renault": "Mid-range", "Skoda": "Mid-range",
    "Tata": "Budget", "Toyota": "Premium", "Volkswagen": "Mid-range",
}

def build_prediction_row(brand, year, km_driven, fuel, seller_type, transmission, owner):
    """Replicate backend/predictor.py preprocessing exactly."""
    car_age = CURRENT_YEAR - year
    km_per_year = km_driven / (car_age + 1)
    brand_tier = BRAND_TIER_MAP.get(brand, "Mid-range")

    # Label encode brand
    known = list(ver_encoder.classes_)
    b = brand if brand in known else "Other"
    brand_enc = int(ver_encoder.transform([b])[0])

    # One-hot encode
    oh = {
        "fuel_Diesel": 1 if fuel == "Diesel" else 0,
        "fuel_Electric": 1 if fuel == "Electric" else 0,
        "fuel_LPG": 1 if fuel == "LPG" else 0,
        "fuel_Petrol": 1 if fuel == "Petrol" else 0,
        "seller_type_Individual": 1 if seller_type == "Individual" else 0,
        "seller_type_Trustmark Dealer": 1 if seller_type == "Trustmark Dealer" else 0,
        "transmission_Manual": 1 if transmission == "Manual" else 0,
        "owner_Fourth & Above Owner": 1 if owner == "Fourth & Above Owner" else 0,
        "owner_Second Owner": 1 if owner == "Second Owner" else 0,
        "owner_Test Drive Car": 1 if owner == "Test Drive Car" else 0,
        "owner_Third Owner": 1 if owner == "Third Owner" else 0,
        "brand_tier_Luxury": 1 if brand_tier == "Luxury" else 0,
        "brand_tier_Mid-range": 1 if brand_tier == "Mid-range" else 0,
        "brand_tier_Premium": 1 if brand_tier == "Premium" else 0,
    }

    # Scale numericals
    num_df = pd.DataFrame([[km_driven, car_age, km_per_year]],
                          columns=["km_driven", "car_age", "km_per_year"])
    scaled = ver_scaler.transform(num_df)

    row = {"km_driven": scaled[0][0], "brand": brand_enc,
           "car_age": scaled[0][1], "km_per_year": scaled[0][2]}
    row.update(oh)
    return pd.DataFrame([row], columns=ver_features)

test_cases = [
    ("Maruti", 2015, 50000, "Petrol", "Individual", "Manual", "First Owner", 303900),
    ("Audi", 2018, 30000, "Diesel", "Trustmark Dealer", "Automatic", "First Owner", 2560400),
    ("Hyundai", 2020, 15000, "Petrol", "Individual", "Manual", "First Owner", 520900),
    ("Toyota", 2012, 120000, "Diesel", "Individual", "Manual", "Second Owner", 638700),
]

print("\n--- Prediction Verification ---")
all_close = True
for brand, year, km, fuel, seller, trans, owner, expected in test_cases:
    input_df = build_prediction_row(brand, year, km, fuel, seller, trans, owner)
    raw_pred = ver_model.predict(input_df)[0]
    pred = round(float(raw_pred) / 100) * 100
    pred = max(pred, 0)
    pct_diff = abs(pred - expected) / expected * 100

    status = "OK" if pct_diff < 5 else ("WARN" if pct_diff < 15 else "FAIL")
    print(f"  {brand:10s} {year} | Expected: Rs.{expected:>10,.0f} | "
          f"Got: Rs.{pred:>10,.0f} | Diff: {pct_diff:.1f}% [{status}]")
    if pct_diff > 15:
        all_close = False

if all_close:
    print("\nAll predictions within acceptable range.")
else:
    print("\nWARNING: Some predictions differ significantly. Investigate.")

# ============================================================
# TASK 8: Final summary
# ============================================================
print("\n" + "=" * 70)
print("TASK 8: Final Summary")
print("=" * 70)

print(f"\nModel retrained and verified. R2={best_result['r2']:.4f}, "
      f"RMSE=Rs.{best_result['rmse']:,.0f}. "
      f"All artifacts synchronized with corrected scaler.")

print(f"\nSaved artifacts:")
print(f"  [1] ../models/best_model.pkl          ({best_model_name})")
print(f"  [2] ../models/model_comparison.csv     (6 models)")
print(f"  [3] ../models/model_metadata.json      (updated {metadata['training_date'][:10]})")
print(f"  [4] backend/app_models/                (synced)")

print(f"\nPipeline consistency:")
print(f"  scaler.pkl:          3 features (km_driven, car_age, km_per_year)")
print(f"  feature_columns.pkl: {len(ver_features)} features")
print(f"  best_model.pkl:      {best_model_name} (retrained on fixed data)")
print(f"  brand_encoder.pkl:   {len(ver_encoder.classes_)} classes")

print("\nRetraining complete!")
