"""
Fix Technical Debt: Refit StandardScaler on 3 columns (without depreciation_rate).

Regenerates the entire preprocessing pipeline from raw data to ensure
the scaler is fitted correctly on [km_driven, car_age, km_per_year] only.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler, LabelEncoder

print("=" * 70)
print("SCALER FIX: Regenerating preprocessing pipeline from raw data")
print("=" * 70)

# ============================================================
# Step 0: Verify current problem
# ============================================================
print("\n--- STEP 0: Verify the problem ---")
old_scaler = joblib.load('../models/scaler.pkl')
print(f"OLD scaler.n_features_in_: {old_scaler.n_features_in_}")
print(f"OLD scaler.feature_names_in_: {list(old_scaler.feature_names_in_)}")
print(f"PROBLEM: Scaler expects {old_scaler.n_features_in_} columns including 'depreciation_rate'")

# Also check current cleaned data
current_df = pd.read_csv('../data/cleaned_car_data.csv')
print(f"\nCurrent cleaned_car_data.csv shape: {current_df.shape}")
print(f"Current columns: {current_df.columns.tolist()}")
has_depreciation = 'depreciation_rate' in current_df.columns
print(f"Has 'depreciation_rate' column: {has_depreciation}")

# ============================================================
# Step 1: Load raw data
# ============================================================
print("\n--- STEP 1: Load raw data ---")
raw_df = pd.read_csv('../data/CAR DETAILS FROM CAR DEKHO.csv')
print(f"Raw dataset loaded: {raw_df.shape}")
print(f"Columns: {raw_df.columns.tolist()}")

# ============================================================
# Step 2a: Drop duplicates
# ============================================================
print("\n--- STEP 2a: Drop duplicates ---")
print(f"Before: {len(raw_df)} rows")
df = raw_df.drop_duplicates().reset_index(drop=True)
print(f"After:  {len(df)} rows (dropped {len(raw_df) - len(df)} duplicates)")

# ============================================================
# Step 2b: Extract 'brand' from 'name' (first word)
# ============================================================
print("\n--- STEP 2b: Extract brand ---")
df['brand'] = df['name'].apply(lambda x: x.split()[0])
print(f"Unique brands: {df['brand'].nunique()} -> {sorted(df['brand'].unique())}")

# ============================================================
# Step 2c: Create 'car_age' = 2024 - year
# ============================================================
print("\n--- STEP 2c: Create car_age ---")
CURRENT_YEAR = 2024
df['car_age'] = CURRENT_YEAR - df['year']
print(f"car_age range: {df['car_age'].min()} to {df['car_age'].max()}")

# ============================================================
# Step 2d: Create brand_tier based on avg selling_price per brand
# ============================================================
print("\n--- STEP 2d: Create brand_tier ---")
brand_avg = df.groupby('brand')['selling_price'].mean()
print("\nBrand avg prices:")
for brand, avg in brand_avg.sort_values(ascending=False).items():
    if avg > 1500000:
        tier = "Luxury"
    elif avg >= 700000:
        tier = "Premium"
    elif avg >= 350000:
        tier = "Mid-range"
    else:
        tier = "Budget"
    print(f"  {brand:20s}: Rs.{avg:>12,.0f} -> {tier}")

def assign_tier(avg_price):
    if avg_price > 1500000:
        return "Luxury"
    elif avg_price >= 700000:
        return "Premium"
    elif avg_price >= 350000:
        return "Mid-range"
    else:
        return "Budget"

brand_tier_map = brand_avg.apply(assign_tier)
df['brand_tier'] = df['brand'].map(brand_tier_map)
print(f"\nBrand tier distribution:\n{df['brand_tier'].value_counts()}")

# ============================================================
# Step 2e: Create 'km_per_year'
# ============================================================
print("\n--- STEP 2e: Create km_per_year ---")
df['km_per_year'] = df['km_driven'] / (df['car_age'] + 1)
print(f"km_per_year range: {df['km_per_year'].min():.0f} to {df['km_per_year'].max():.0f}")

# ============================================================
# Step 2f: Reduce brand cardinality (brands with <30 -> "Other")
# ============================================================
print("\n--- STEP 2f: Reduce brand cardinality ---")
brand_counts = df['brand'].value_counts()
small_brands = brand_counts[brand_counts < 30].index.tolist()
print(f"Brands with <30 listings (mapped to 'Other'): {small_brands}")
df['brand'] = df['brand'].apply(lambda x: 'Other' if x in small_brands else x)
print(f"Final brands: {sorted(df['brand'].unique())}")
print(f"Brand count: {df['brand'].nunique()}")

# Check if this matches the existing encoder
existing_encoder = joblib.load('../models/brand_encoder.pkl')
existing_classes = list(existing_encoder.classes_)
new_classes = sorted(df['brand'].unique())
print(f"\nExisting encoder classes: {existing_classes}")
print(f"New classes:             {new_classes}")
classes_match = existing_classes == new_classes
print(f"Classes match: {classes_match}")

# ============================================================
# Step 2g: Cap outliers at 99th percentile
# ============================================================
print("\n--- STEP 2g: Cap outliers at 99th percentile ---")
for col in ['selling_price', 'km_driven']:
    p99 = df[col].quantile(0.99)
    before_count = (df[col] > p99).sum()
    df[col] = df[col].clip(upper=p99)
    print(f"  {col}: capped at {p99:,.0f} ({before_count} values clipped)")

# Recompute km_per_year after capping km_driven
df['km_per_year'] = df['km_driven'] / (df['car_age'] + 1)

# ============================================================
# Step 2h: One-hot encode categoricals (drop_first=True)
# ============================================================
print("\n--- STEP 2h: One-hot encode categoricals ---")
categorical_cols = ['fuel', 'seller_type', 'transmission', 'owner', 'brand_tier']
print(f"Encoding: {categorical_cols}")

for col in categorical_cols:
    print(f"  {col}: {sorted(df[col].unique())}")

df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
print(f"Shape after encoding: {df_encoded.shape}")

# ============================================================
# Step 2i: Label encode 'brand'
# ============================================================
print("\n--- STEP 2i: Label encode brand ---")
if classes_match:
    # Reuse existing encoder
    brand_encoder = existing_encoder
    print("Reusing existing brand_encoder.pkl (classes match)")
else:
    # Refit
    brand_encoder = LabelEncoder()
    brand_encoder.fit(sorted(df_encoded['brand'].unique()))
    print(f"Refit brand_encoder with classes: {list(brand_encoder.classes_)}")

df_encoded['brand'] = brand_encoder.transform(df_encoded['brand'])
print(f"Brand encoded values: {sorted(df_encoded['brand'].unique())}")

# ============================================================
# Step 2j: Drop original columns
# ============================================================
print("\n--- STEP 2j: Drop original columns ---")
cols_to_drop = ['name', 'year']
# Only drop columns that exist
cols_to_drop = [c for c in cols_to_drop if c in df_encoded.columns]
df_encoded = df_encoded.drop(columns=cols_to_drop)
print(f"Dropped: {cols_to_drop}")
print(f"Shape after dropping: {df_encoded.shape}")
print(f"Columns: {df_encoded.columns.tolist()}")

# NOTE: NOT creating depreciation_rate at all

# ============================================================
# Step 3: Verify pre-scaling state
# ============================================================
print("\n--- STEP 3: Pre-scaling verification ---")
numerical_features = ['km_driven', 'car_age', 'km_per_year']
print(f"Numerical features (BEFORE scaling):")
for col in numerical_features:
    print(f"  {col}: mean={df_encoded[col].mean():.2f}, std={df_encoded[col].std():.2f}, "
          f"min={df_encoded[col].min():.2f}, max={df_encoded[col].max():.2f}")

# ============================================================
# Step 4: Fit NEW StandardScaler on ONLY 3 columns
# ============================================================
print("\n--- STEP 4: Fit new StandardScaler on 3 columns ---")
new_scaler = StandardScaler()
new_scaler.fit(df_encoded[numerical_features])
print(f"New scaler fitted on: {list(new_scaler.feature_names_in_)}")
print(f"New scaler.n_features_in_: {new_scaler.n_features_in_}")
print(f"Means: {new_scaler.mean_}")
print(f"Scales: {new_scaler.scale_}")

# ============================================================
# Step 5: Apply scaling
# ============================================================
print("\n--- STEP 5: Apply scaler.transform ---")
df_encoded[numerical_features] = new_scaler.transform(df_encoded[numerical_features])
print("Scaling applied to km_driven, car_age, km_per_year")

# ============================================================
# Step 6: Verify final dataframe
# ============================================================
print("\n--- STEP 6: Final verification ---")
print(f"Final shape: {df_encoded.shape}")
print(f"Expected:    (3577, 19)")
print(f"Shape correct: {df_encoded.shape == (3577, 19)}")

print(f"\nFinal columns ({len(df_encoded.columns)}):")
print(f"  {df_encoded.columns.tolist()}")

# Compare with expected feature columns
expected_feature_cols = joblib.load('../models/feature_columns.pkl')
actual_feature_cols = [c for c in df_encoded.columns if c != 'selling_price']
print(f"\nExpected features: {expected_feature_cols}")
print(f"Actual features:   {actual_feature_cols}")

# Check if they match (order-independent first)
set_match = set(expected_feature_cols) == set(actual_feature_cols)
print(f"Feature sets match: {set_match}")

# If column order differs, reorder to match
if set_match and actual_feature_cols != expected_feature_cols:
    print("Reordering columns to match expected order...")
    col_order = ['selling_price'] + expected_feature_cols
    df_encoded = df_encoded[col_order]
    actual_feature_cols = [c for c in df_encoded.columns if c != 'selling_price']
    print(f"Reordered features: {actual_feature_cols}")

order_match = actual_feature_cols == expected_feature_cols
print(f"Feature order match: {order_match}")

print(f"\nMissing values: {df_encoded.isnull().sum().sum()}")

print(f"\nScaled columns statistics (should be mean~0, std~1):")
for col in numerical_features:
    print(f"  {col}: mean={df_encoded[col].mean():.4f}, std={df_encoded[col].std():.4f}")

# ============================================================
# Step 7: Save corrected artifacts
# ============================================================
print("\n--- STEP 7: Save corrected artifacts ---")
os.makedirs('../models', exist_ok=True)

# Save cleaned data
df_encoded.to_csv('../data/cleaned_car_data.csv', index=False)
print(f"Saved: ../data/cleaned_car_data.csv ({df_encoded.shape})")

# Save new scaler (THE FIX)
joblib.dump(new_scaler, '../models/scaler.pkl')
print(f"Saved: ../models/scaler.pkl (fitted on {list(new_scaler.feature_names_in_)})")

# Save brand encoder (only if refit)
if not classes_match:
    joblib.dump(brand_encoder, '../models/brand_encoder.pkl')
    print(f"Saved: ../models/brand_encoder.pkl (REFIT)")
else:
    print(f"Skipped: ../models/brand_encoder.pkl (classes unchanged)")

# Save feature columns
feature_cols_list = actual_feature_cols
joblib.dump(feature_cols_list, '../models/feature_columns.pkl')
print(f"Saved: ../models/feature_columns.pkl ({len(feature_cols_list)} features)")

print("\nScaler refit on 3 columns successfully. Old 4-column scaler replaced.")

# ============================================================
# Step 8: Verification
# ============================================================
print("\n--- STEP 8: Verification ---")
verify_scaler = joblib.load('../models/scaler.pkl')
print(f"Loaded scaler.n_features_in_: {verify_scaler.n_features_in_}")
print(f"Loaded scaler.feature_names_in_: {list(verify_scaler.feature_names_in_)}")
expected_numerical = ['km_driven', 'car_age', 'km_per_year']
print(f"Expected: {expected_numerical}")
print(f"Match: {list(verify_scaler.feature_names_in_) == expected_numerical}")

# Quick inference test
test_row = pd.DataFrame(
    [[50000, 9, 5000]],
    columns=['km_driven', 'car_age', 'km_per_year']
)
scaled = verify_scaler.transform(test_row)
print(f"\nInference test: {test_row.values[0]} -> {scaled[0]}")
print("No shape mismatch errors!")

# Also copy to backend/app_models/
backend_models = '../backend/app_models'
if os.path.isdir(backend_models):
    import shutil
    for f in ['scaler.pkl', 'brand_encoder.pkl', 'feature_columns.pkl']:
        src = f'../models/{f}'
        dst = os.path.join(backend_models, f)
        shutil.copy2(src, dst)
        print(f"Copied {f} -> {backend_models}/")
    # Also copy cleaned_car_data.csv is not needed for backend

print("\n" + "=" * 70)
print("FIX COMPLETE: Scaler now expects 3 columns (no depreciation_rate)")
print("=" * 70)
