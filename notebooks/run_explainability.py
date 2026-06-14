"""
Car Price Prediction - SHAP Explainability
Standalone script to run all explainability analysis.
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split

try:
    import shap
    print(f"SHAP version: {shap.__version__}")
except ImportError:
    print("SHAP not found. Install with: pip install shap")
    sys.exit(1)

print("All libraries imported successfully")

# ============================================================
# Section 2: Load Artifacts
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: LOAD ARTIFACTS")
print("=" * 60)

model = joblib.load('../models/best_model.pkl')
print(f"Model loaded: {type(model).__name__}")

feature_columns = joblib.load('../models/feature_columns.pkl')
scaler = joblib.load('../models/scaler.pkl')
brand_encoder = joblib.load('../models/brand_encoder.pkl')
print(f"Feature columns ({len(feature_columns)}): {feature_columns}")
print(f"Scaler: {type(scaler).__name__}")
print(f"Brand encoder classes: {brand_encoder.classes_.tolist()}")

df = pd.read_csv('../data/cleaned_car_data.csv')
X = df.drop(columns=['selling_price'])
y = df['selling_price']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nDataset shape: {df.shape}")
print(f"X_train: {X_train.shape}, X_test: {X_test.shape}")

# ============================================================
# Section 3: Create SHAP Explainer
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: CREATE SHAP EXPLAINER")
print("=" * 60)

explainer = shap.TreeExplainer(model)
print(f"Explainer created: {type(explainer).__name__}")
base_val = float(np.atleast_1d(explainer.expected_value).flatten()[0])
print(f"Expected value (base price): Rs.{base_val:,.0f}")

sample_size = min(200, len(X_test))
X_test_sample = X_test.iloc[:sample_size].copy()
y_test_sample = y_test.iloc[:sample_size].copy()

print(f"\nComputing SHAP values for {sample_size} test samples...")
shap_values = explainer.shap_values(X_test_sample)

print(f"SHAP values shape: {shap_values.shape}")
print(f"X_test_sample shape: {X_test_sample.shape}")
print(f"Shapes match: {shap_values.shape == X_test_sample.shape}")

# ============================================================
# Section 4: Global Feature Importance
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: GLOBAL FEATURE IMPORTANCE (SHAP)")
print("=" * 60)

os.makedirs('../models', exist_ok=True)

# Bar plot
plt.figure(figsize=(10, 7))
shap.summary_plot(
    shap_values, X_test_sample,
    plot_type='bar',
    max_display=15,
    show=False
)
plt.title('SHAP Global Feature Importance (Mean |SHAP Value|)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('../models/shap_summary_bar.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved shap_summary_bar.png")

# Dot/Beeswarm plot
plt.figure(figsize=(10, 7))
shap.summary_plot(
    shap_values, X_test_sample,
    plot_type='dot',
    max_display=15,
    show=False
)
plt.title('SHAP Feature Impact Distribution (Beeswarm)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('../models/shap_summary_dot.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved shap_summary_dot.png")

# Print top features
mean_abs_shap = np.abs(shap_values).mean(axis=0)
feature_importance_shap = pd.DataFrame({
    'feature': X_test_sample.columns,
    'mean_abs_shap': mean_abs_shap
}).sort_values('mean_abs_shap', ascending=False)

print("\nTop 15 Features by Mean |SHAP Value|:")
print(feature_importance_shap.head(15).to_string(index=False))

# ============================================================
# Section 5: Local Explanation (Single Prediction)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: SINGLE PREDICTION EXPLANATION")
print("=" * 60)

row_idx = 0
single_row = X_test_sample.iloc[row_idx]
actual_price = y_test_sample.iloc[row_idx]
predicted_price = model.predict(X_test_sample.iloc[[row_idx]])[0]

print(f"Actual Selling Price:    Rs.{actual_price:,.0f}")
print(f"Predicted Selling Price: Rs.{predicted_price:,.0f}")
print(f"Base Value (avg price):  Rs.{base_val:,.0f}")
print(f"Prediction Error:        Rs.{abs(actual_price - predicted_price):,.0f}")

# Waterfall plot
shap_explanation = shap.Explanation(
    values=shap_values[row_idx],
    base_values=base_val,
    data=single_row.values,
    feature_names=X_test_sample.columns.tolist()
)

plt.figure(figsize=(10, 7))
shap.plots.waterfall(shap_explanation, max_display=15, show=False)
plt.title(f'SHAP Waterfall - Predicted Rs.{predicted_price:,.0f} Actual Rs.{actual_price:,.0f}',
          fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('../models/shap_waterfall_example.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nSaved shap_waterfall_example.png")

# ============================================================
# Section 6: Reusable Explanation Function
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: REUSABLE EXPLANATION FUNCTION")
print("=" * 60)

def explain_prediction(model, explainer, input_row_df, feature_names):
    predicted_price = float(model.predict(input_row_df)[0])
    sv = explainer.shap_values(input_row_df)
    if len(sv.shape) == 1:
        shap_vals = sv
    else:
        shap_vals = sv[0]

    base_value = float(np.atleast_1d(explainer.expected_value).flatten()[0])

    explanations = []
    for i, fname in enumerate(feature_names):
        val = float(shap_vals[i])
        explanations.append({
            'feature': fname,
            'shap_value': round(val, 2),
            'impact': 'increases' if val > 0 else 'decreases'
        })

    explanations.sort(key=lambda x: abs(x['shap_value']), reverse=True)
    explanations = explanations[:10]

    return {
        'explanations': explanations,
        'base_value': round(base_value, 2),
        'predicted_price': round(predicted_price, 2)
    }

test_row = X_test_sample.iloc[[0]]
result = explain_prediction(model, explainer, test_row, X_test_sample.columns.tolist())

print("explain_prediction() output for test row #0:")
print(json.dumps(result, indent=2))

# ============================================================
# Section 7: Human-Readable Explanation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: HUMAN-READABLE EXPLANATION")
print("=" * 60)

FEATURE_LABELS = {
    'km_driven': 'Kilometers Driven',
    'brand': 'Car Brand',
    'car_age': 'Vehicle Age',
    'km_per_year': 'Yearly Usage (km/year)',
    'fuel_Diesel': 'Diesel Fuel',
    'fuel_Electric': 'Electric Vehicle',
    'fuel_LPG': 'LPG Fuel',
    'fuel_Petrol': 'Petrol Fuel',
    'seller_type_Individual': 'Individual Seller',
    'seller_type_Trustmark Dealer': 'Trustmark Dealer',
    'transmission_Manual': 'Manual Transmission',
    'owner_Fourth & Above Owner': 'Fourth+ Owner',
    'owner_Second Owner': 'Second Owner',
    'owner_Test Drive Car': 'Test Drive Car',
    'owner_Third Owner': 'Third Owner',
    'brand_tier_Luxury': 'Luxury Brand',
    'brand_tier_Mid-range': 'Mid-Range Brand',
    'brand_tier_Premium': 'Premium Brand'
}


def format_explanation(explanation_list, base_value, predicted_price, feature_labels=None):
    if feature_labels is None:
        feature_labels = {}

    lines = []
    lines.append(f"Predicted Price: Rs.{predicted_price:,.0f}")
    lines.append(f"Base Price (average): Rs.{base_value:,.0f}")
    lines.append("")
    lines.append("Key factors:")

    for item in explanation_list:
        fname = item['feature']
        label = feature_labels.get(fname, fname)
        shap_val = item['shap_value']
        impact = item['impact']

        if shap_val > 0:
            lines.append(f"  + {label}: +Rs.{abs(shap_val):,.0f} ({impact} price)")
        else:
            lines.append(f"  - {label}: -Rs.{abs(shap_val):,.0f} ({impact} price)")

    return "\n".join(lines)


formatted = format_explanation(
    result['explanations'],
    result['base_value'],
    result['predicted_price'],
    FEATURE_LABELS
)

print(formatted)

# ============================================================
# Section 8: Save Explainer
# ============================================================
print("\n" + "=" * 60)
print("SECTION 8: SAVE EXPLAINER FOR API USE")
print("=" * 60)

try:
    explainer_path = '../models/shap_explainer.pkl'
    joblib.dump(explainer, explainer_path)
    print(f"Saved SHAP explainer to: {explainer_path}")

    test_explainer = joblib.load(explainer_path)
    print(f"Verification: Loaded explainer type = {type(test_explainer).__name__}")
    test_base = float(np.atleast_1d(test_explainer.expected_value).flatten()[0])
    print(f"Verification: Expected value = Rs.{test_base:,.0f}")
    print("SHAP explainer saved and verified successfully!")

except Exception as e:
    print(f"Warning: Could not pickle explainer: {e}")
    print("The explainer can be recreated at API startup with:")
    print("  explainer = shap.TreeExplainer(model)")

# Save feature labels
labels_path = '../models/feature_labels.json'
with open(labels_path, 'w') as f:
    json.dump(FEATURE_LABELS, f, indent=2)
print(f"\nSaved feature labels to: {labels_path}")

# ============================================================
# Section 9: Final Summary
# ============================================================
print("\n" + "=" * 60)
print("SECTION 9: FINAL SUMMARY")
print("=" * 60)

print("\nTop 5 Most Important Features (Global SHAP):")
for i, row in feature_importance_shap.head(5).iterrows():
    print(f"  {i+1}. {FEATURE_LABELS.get(row['feature'], row['feature'])} "
          f"({row['feature']}) - Mean |SHAP| = Rs.{row['mean_abs_shap']:,.0f}")

print("\nAll saved artifacts:")
print("  [1] ../models/shap_explainer.pkl")
print("  [2] ../models/shap_summary_bar.png")
print("  [3] ../models/shap_summary_dot.png")
print("  [4] ../models/shap_waterfall_example.png")
print("  [5] ../models/feature_labels.json")

print("\nExplainability pipeline completed successfully!")
print("Ready for FastAPI backend integration.")
