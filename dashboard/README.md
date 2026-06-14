# 📊 Car Price Prediction Dashboard

A Streamlit web application that serves as the frontend for the Car Price Prediction API.
It allows users to input car details, get a predicted selling price, and view a SHAP-based explanation of the factors influencing the price.

---

## Quick Start

### 1. Ensure the Backend is Running
The dashboard requires the FastAPI backend to be running.
```bash
cd ../backend
uvicorn main:app --reload --port 8000
```

### 2. Install Dashboard Dependencies
```bash
cd ../dashboard
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```

### 4. View in Browser
Streamlit will automatically open your default web browser to `http://localhost:8501`.

---

## Features

- **Interactive Inputs**: Sidebar for easy entry of car features (Brand, Year, km, Fuel, etc.).
- **Live Predictions**: Communicates with the FastAPI backend to get real-time price predictions.
- **SHAP Explanations**: Visualizes the model's decision-making process using an interactive Waterfall chart.
- **Model Insights**: A dedicated tab showing global feature importance and model performance metrics (R², RMSE).
