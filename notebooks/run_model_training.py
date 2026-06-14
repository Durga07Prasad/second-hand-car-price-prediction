"""
Car Price Prediction - Model Training & Evaluation
Standalone script to train all models, compare, and save artifacts.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns
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

# Try-except for optional advanced models
try:
    import xgboost as xgb
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠ XGBoost not found. Install with: pip install xgboost")

try:
    import lightgbm as lgb
    from lightgbm import LGBMRegressor
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠ LightGBM not found. Install with: pip install lightgbm")

try:
    from catboost import CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("⚠ CatBoost not found. Install with: pip install catboost")

print("✓ Core libraries imported successfully")
print(f"XGBoost: {'✓' if XGBOOST_AVAILABLE else '✗'}")
print(f"LightGBM: {'✓' if LIGHTGBM_AVAILABLE else '✗'}")
print(f"CatBoost: {'✓' if CATBOOST_AVAILABLE else '✗'}")

# ============================================================
# Section 2: Load Data
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: LOAD DATA")
print("=" * 70)

df = pd.read_csv('../data/cleaned_car_data.csv')

print(f"Dataset loaded: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nMissing values: {df.isnull().sum().sum()}")

X = df.drop(columns=['selling_price'])
y = df['selling_price']

print(f"\nFeatures (X): {X.shape} - {X.columns.tolist()}")
print(f"Target (y): {y.shape}")
print(f"\nTarget statistics:")
print(y.describe())

# ============================================================
# Section 3: Train-Test Split
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: TRAIN-TEST SPLIT")
print("=" * 70)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"X_train shape: {X_train.shape}")
print(f"X_test shape: {X_test.shape}")
print(f"y_train shape: {y_train.shape}")
print(f"y_test shape: {y_test.shape}")

# ============================================================
# Section 4: Evaluation Function
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: EVALUATION FUNCTION DEFINED")
print("=" * 70)

def evaluate_model(model_name, model, X_train, X_test, y_train, y_test):
    """
    Train and evaluate a model with test metrics and cross-validation.
    """
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    cv_fold = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv_fold, scoring='r2')
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()

    print(f"[{model_name:20}] RMSE: Rs.{rmse:>12,.0f} | MAE: Rs.{mae:>12,.0f} | R2: {r2:.4f} | CV R2: {cv_mean:.4f} (+/-{cv_std:.4f})")

    return {
        'model_name': model_name,
        'model': model,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'cv_mean': cv_mean,
        'cv_std': cv_std
    }

print("✓ evaluate_model() function ready")

# ============================================================
# Section 5: Baseline Models
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: TRAINING BASELINE MODELS")
print("=" * 70)

results = []

lr_model = LinearRegression()
results.append(evaluate_model("Linear Regression", lr_model, X_train, X_test, y_train, y_test))

dt_model = DecisionTreeRegressor(random_state=42, max_depth=10)
results.append(evaluate_model("Decision Tree", dt_model, X_train, X_test, y_train, y_test))

# ============================================================
# Section 6: Advanced Models
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: TRAINING ADVANCED MODELS")
print("=" * 70)

rf_model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
results.append(evaluate_model("Random Forest", rf_model, X_train, X_test, y_train, y_test))

if XGBOOST_AVAILABLE:
    xgb_model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42)
    results.append(evaluate_model("XGBoost", xgb_model, X_train, X_test, y_train, y_test))
else:
    print("[XGBoost             ] Skipped (not installed)")

if LIGHTGBM_AVAILABLE:
    lgb_model = LGBMRegressor(n_estimators=200, learning_rate=0.05, random_state=42, verbose=-1)
    results.append(evaluate_model("LightGBM", lgb_model, X_train, X_test, y_train, y_test))
else:
    print("[LightGBM            ] Skipped (not installed)")

if CATBOOST_AVAILABLE:
    cb_model = CatBoostRegressor(iterations=200, learning_rate=0.05, random_state=42, verbose=0)
    results.append(evaluate_model("CatBoost", cb_model, X_train, X_test, y_train, y_test))
else:
    print("[CatBoost            ] Skipped (not installed)")

print(f"\n✓ Total models trained: {len(results)}")

# ============================================================
# Section 7: Model Comparison Table
# ============================================================
print("\n" + "=" * 70)
print("SECTION 7: MODEL COMPARISON TABLE")
print("=" * 70)

comparison_data = [
    {
        'Model': r['model_name'],
        'RMSE': r['rmse'],
        'MAE': r['mae'],
        'R2': r['r2'],
        'CV_R2_mean': r['cv_mean'],
        'CV_R2_std': r['cv_std']
    }
    for r in results
]

comparison_df = pd.DataFrame(comparison_data)
comparison_df = comparison_df.sort_values('R2', ascending=False).reset_index(drop=True)

display_df = comparison_df.copy()
display_df['RMSE'] = display_df['RMSE'].apply(lambda x: f"Rs.{x:,.0f}")
display_df['MAE'] = display_df['MAE'].apply(lambda x: f"Rs.{x:,.0f}")
display_df['R2'] = display_df['R2'].apply(lambda x: f"{x:.4f}")
display_df['CV_R2_mean'] = display_df['CV_R2_mean'].apply(lambda x: f"{x:.4f}")
display_df['CV_R2_std'] = display_df['CV_R2_std'].apply(lambda x: f"{x:.4f}")

print("\n" + display_df.to_string(index=False))

# Bar charts
os.makedirs('../models', exist_ok=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

comparison_sorted_r2 = comparison_df.sort_values('R2')
ax1.barh(comparison_sorted_r2['Model'], comparison_sorted_r2['R2'], color='steelblue')
ax1.set_xlabel('R2 Score (Test Set)', fontsize=11, fontweight='bold')
ax1.set_title('Model R2 Score Comparison', fontsize=12, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)
for i, v in enumerate(comparison_sorted_r2['R2']):
    ax1.text(v - 0.01, i, f' {v:.4f}', va='center', ha='right', fontweight='bold', color='white')

comparison_sorted_rmse = comparison_df.sort_values('RMSE')
ax2.barh(comparison_sorted_rmse['Model'], comparison_sorted_rmse['RMSE'], color='coral')
ax2.set_xlabel('RMSE (Rs.)', fontsize=11, fontweight='bold')
ax2.set_title('Model RMSE Comparison (Lower is Better)', fontsize=12, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('../models/model_comparison.png', dpi=100, bbox_inches='tight')
plt.close()
print("\n✓ Saved model_comparison.png successfully")

# ============================================================
# Section 8: Best Model Selection
# ============================================================
print("\n" + "=" * 70)
print("SECTION 8: BEST MODEL SELECTION")
print("=" * 70)

best_result = max(results, key=lambda x: x['r2'])
best_model = best_result['model']
best_model_name = best_result['model_name']

print(f"\n*** BEST MODEL: {best_model_name} ***")
print(f"Test RMSE: Rs.{best_result['rmse']:,.0f}")
print(f"Test MAE:  Rs.{best_result['mae']:,.0f}")
print(f"Test R2:   {best_result['r2']:.4f}")
print(f"CV R2 (5-fold): {best_result['cv_mean']:.4f} (+/-{best_result['cv_std']:.4f})")

y_pred_best = best_model.predict(X_test)

# Actual vs Predicted + Residual plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.scatter(y_test, y_pred_best, alpha=0.6, s=30, color='steelblue', edgecolors='navy', linewidth=0.5)
min_val = min(y_test.min(), y_pred_best.min())
max_val = max(y_test.max(), y_pred_best.max())
ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
ax1.set_xlabel('Actual Selling Price (Rs.)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Predicted Selling Price (Rs.)', fontsize=11, fontweight='bold')
ax1.set_title(f'{best_model_name} - Actual vs Predicted', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(alpha=0.3)

residuals = y_test.values - y_pred_best
ax2.hist(residuals, bins=50, color='steelblue', edgecolor='navy', alpha=0.7)
ax2.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero Error')
ax2.set_xlabel('Residuals (Rs.)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax2.set_title('Residual Distribution', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('../models/best_model_predictions.png', dpi=100, bbox_inches='tight')
plt.close()
print("\n✓ Saved best_model_predictions.png successfully")

print(f"\nResidual Statistics:")
print(f"Mean: Rs.{residuals.mean():,.0f}")
print(f"Std Dev: Rs.{residuals.std():,.0f}")
print(f"Min: Rs.{residuals.min():,.0f}")
print(f"Max: Rs.{residuals.max():,.0f}")

# ============================================================
# Section 9: Feature Importance
# ============================================================
print("\n" + "=" * 70)
print("SECTION 9: FEATURE IMPORTANCE")
print("=" * 70)

if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=True)

    feature_importance_top15 = feature_importance.tail(15)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(feature_importance_top15['feature'], feature_importance_top15['importance'], color='steelblue')
    ax.set_xlabel('Importance Score', fontsize=11, fontweight='bold')
    ax.set_title(f'{best_model_name} - Top 15 Feature Importance', fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('../models/feature_importance.png', dpi=100, bbox_inches='tight')
    plt.close()
    print("✓ Saved feature_importance.png successfully")

    print("\nTOP 15 FEATURES:")
    print(feature_importance_top15.to_string(index=False))

elif best_model_name == 'Linear Regression':
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': np.abs(best_model.coef_)
    }).sort_values('importance', ascending=True)

    feature_importance_top15 = feature_importance.tail(15)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(feature_importance_top15['feature'], feature_importance_top15['importance'], color='steelblue')
    ax.set_xlabel('|Coefficient| (Absolute Value)', fontsize=11, fontweight='bold')
    ax.set_title(f'{best_model_name} - Top 15 Feature Importance (|Coefficients|)', fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('../models/feature_importance.png', dpi=100, bbox_inches='tight')
    plt.close()
    print("✓ Saved feature_importance.png successfully")

    print("\nTOP 15 FEATURES (by absolute coefficient):")
    print(feature_importance_top15.to_string(index=False))
else:
    print(f"Model {best_model_name} does not support feature importance extraction.")

# ============================================================
# Section 10: Save Artifacts
# ============================================================
print("\n" + "=" * 70)
print("SECTION 10: SAVE ARTIFACTS")
print("=" * 70)

# 1. Save best model
best_model_path = '../models/best_model.pkl'
joblib.dump(best_model, best_model_path)
print(f"✓ Saved best_model.pkl successfully -> {best_model_path}")

# 2. Save comparison table
comparison_csv_path = '../models/model_comparison.csv'
comparison_df.to_csv(comparison_csv_path, index=False)
print(f"✓ Saved model_comparison.csv successfully -> {comparison_csv_path}")

# 3. Save metadata
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

metadata_path = '../models/model_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"✓ Saved model_metadata.json successfully -> {metadata_path}")

# ============================================================
# Section 11: Final Summary
# ============================================================
print("\n" + "=" * 70)
print("SECTION 11: FINAL SUMMARY")
print("=" * 70)

print("\n--- FINAL MODEL COMPARISON (sorted by R2 descending) ---\n")
print(display_df.to_string(index=False))

print(f"\n{'='*70}")
print(f"WINNER: {best_model_name}")
print(f"{'='*70}")
print(f"  - Achieved the highest Test R2 of {best_result['r2']:.4f}")
print(f"  - RMSE of Rs.{best_result['rmse']:,.0f} means predictions are off by ~Rs.{best_result['rmse']:,.0f} on average (RMSE)")
print(f"  - MAE of Rs.{best_result['mae']:,.0f} means the average absolute error is Rs.{best_result['mae']:,.0f}")
print(f"  - CV R2 of {best_result['cv_mean']:.4f} (+/-{best_result['cv_std']:.4f}) confirms stability across folds")
print(f"{'='*70}")

print("\nAll artifacts saved:")
print(f"  [1] ../models/best_model.pkl")
print(f"  [2] ../models/model_comparison.csv")
print(f"  [3] ../models/model_metadata.json")
print(f"  [4] ../models/model_comparison.png")
print(f"  [5] ../models/best_model_predictions.png")
print(f"  [6] ../models/feature_importance.png")

print("\n✓ Model training pipeline completed successfully!")
