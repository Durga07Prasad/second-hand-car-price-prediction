import requests
import json
import os

BASE_URL = "http://localhost:8000"

results = []

def record(endpoint, status_code, passed, notes):
    results.append({"endpoint": endpoint, "status_code": status_code, "passed": passed, "notes": notes})

def run_tests():
    # 1. GET /health
    try:
        r = requests.get(f"{BASE_URL}/health")
        data = r.json()
        passed = r.status_code == 200 and data.get("status") == "healthy" and data.get("model_loaded") is True
        record("GET /health", r.status_code, passed, f"status: {data.get('status')}")
    except Exception as e:
        record("GET /health", "ERROR", False, str(e))

    # 2. GET /model-info
    try:
        r = requests.get(f"{BASE_URL}/model-info")
        data = r.json()
        passed = r.status_code == 200 and "r2_score" in data
        record("GET /model-info", r.status_code, passed, f"r2: {data.get('r2_score')}")
    except Exception as e:
        record("GET /model-info", "ERROR", False, str(e))

    # 3. GET /feature-importance
    try:
        r = requests.get(f"{BASE_URL}/feature-importance")
        data = r.json()
        passed = r.status_code == 200 and len(data) == 15
        record("GET /feature-importance", r.status_code, passed, f"{len(data)} items")
    except Exception as e:
        record("GET /feature-importance", "ERROR", False, str(e))

    # 4. POST /predict
    payload = {
        "brand": "Maruti", "year": 2018, "km_driven": 40000, 
        "fuel": "Petrol", "seller_type": "Individual", 
        "transmission": "Manual", "owner": "First Owner"
    }
    try:
        r = requests.post(f"{BASE_URL}/predict", json=payload)
        data = r.json()
        price = data.get("predicted_price", 0)
        passed = r.status_code == 200 and price > 0
        record("POST /predict", r.status_code, passed, f"Price: {price}")
    except Exception as e:
        record("POST /predict", "ERROR", False, str(e))

    # 5. POST /predict-with-explanation
    try:
        r = requests.post(f"{BASE_URL}/predict-with-explanation", json=payload)
        data = r.json()
        factors = data.get("top_factors", [])
        text = data.get("explanation_text", "")
        passed = r.status_code == 200 and len(factors) == 5 and len(text) > 0
        record("POST /predict-with-explanation", r.status_code, passed, f"Factors: {len(factors)}")
    except Exception as e:
        record("POST /predict-with-explanation", "ERROR", False, str(e))

    # 6. GET /predictions/history?limit=5
    history_id = None
    try:
        r = requests.get(f"{BASE_URL}/predictions/history?limit=5")
        data = r.json()
        predictions = data.get("predictions", [])
        passed = r.status_code == 200 and len(predictions) > 0
        if passed:
            history_id = predictions[0]["id"]
        record("GET /predictions/history", r.status_code, passed, f"Count: {len(predictions)}")
    except Exception as e:
        record("GET /predictions/history", "ERROR", False, str(e))

    # 7. GET /predictions/stats
    try:
        r = requests.get(f"{BASE_URL}/predictions/stats")
        data = r.json()
        total = data.get("total_predictions", 0)
        passed = r.status_code == 200 and total >= 2
        record("GET /predictions/stats", r.status_code, passed, f"Total: {total}")
    except Exception as e:
        record("GET /predictions/stats", "ERROR", False, str(e))

    # 8. POST /feedback
    try:
        if history_id:
            r = requests.post(f"{BASE_URL}/feedback", json={"prediction_id": history_id, "rating": 5, "comment": "test"})
            data = r.json()
            passed = r.status_code == 200 and data.get("status") == "success"
            record("POST /feedback", r.status_code, passed, f"Status: {data.get('status')}")
        else:
            record("POST /feedback", "SKIP", False, "No history ID available")
    except Exception as e:
        record("POST /feedback", "ERROR", False, str(e))

    # Print results table
    print(f"{'Endpoint':<35} | {'Status':<6} | {'Result':<6} | {'Notes'}")
    print("-" * 75)
    for res in results:
        res_str = "PASS" if res["passed"] else "FAIL"
        print(f"{res['endpoint']:<35} | {res['status_code']:<6} | {res_str:<6} | {res['notes']}")

if __name__ == "__main__":
    run_tests()
