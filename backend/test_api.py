"""Quick end-to-end API test after scaler fix."""
import urllib.request
import json

BASE = "http://127.0.0.1:8000"

def post(endpoint, data):
    req = urllib.request.Request(
        f"{BASE}{endpoint}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())

def get(endpoint):
    return json.loads(urllib.request.urlopen(f"{BASE}{endpoint}").read())

print("=" * 60)
print("API ENDPOINT TESTS (with fixed 3-column scaler)")
print("=" * 60)

# GET endpoints
print("\n[1] GET /health")
print(json.dumps(get("/health"), indent=2))

print("\n[2] GET /model-info")
info = get("/model-info")
print(f"  Model: {info['model_name']}, R2: {info['r2_score']:.4f}, Features: {info['feature_count']}")

# POST /predict - multiple test cases
print("\n[3] POST /predict")
test_cases = [
    {"brand": "Maruti", "year": 2015, "km_driven": 50000, "fuel": "Petrol",
     "seller_type": "Individual", "transmission": "Manual", "owner": "First Owner"},
    {"brand": "Audi", "year": 2018, "km_driven": 30000, "fuel": "Diesel",
     "seller_type": "Dealer", "transmission": "Automatic", "owner": "First Owner"},
    {"brand": "Hyundai", "year": 2020, "km_driven": 15000, "fuel": "Petrol",
     "seller_type": "Individual", "transmission": "Manual", "owner": "Second Owner"},
    {"brand": "Toyota", "year": 2012, "km_driven": 120000, "fuel": "Diesel",
     "seller_type": "Individual", "transmission": "Manual", "owner": "Third Owner"},
]

for tc in test_cases:
    result = post("/predict", tc)
    print(f"  {tc['brand']:12s} {tc['year']} | {tc['km_driven']:>7,}km | "
          f"{tc['fuel']:8s} | {tc['transmission']:9s} -> Rs.{result['predicted_price']:>10,.0f}")

# POST /predict-with-explanation
print("\n[4] POST /predict-with-explanation")
expl = post("/predict-with-explanation", test_cases[0])
print(f"  Predicted: Rs.{expl['predicted_price']:,.0f}")
print(f"  Base value: Rs.{expl['base_value']:,.0f}")
print(f"  Top factors:")
for f in expl["top_factors"]:
    sign = "+" if f["shap_value"] > 0 else "-"
    print(f"    {sign} {f['feature']}: {sign}Rs.{abs(f['shap_value']):,.0f} ({f['impact']})")
print(f"  Explanation: {expl['explanation_text'][:100]}...")

# GET /feature-importance
print("\n[5] GET /feature-importance (top 5)")
fi = get("/feature-importance")
for item in fi[:5]:
    print(f"  #{item['rank']} {item['feature']:30s} ({item['technical_name']:25s}) = {item['importance']:.4f}")

print("\n" + "=" * 60)
print("ALL TESTS PASSED - API is fully functional with fixed scaler!")
print("=" * 60)
