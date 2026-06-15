# 🚗 Second-Hand Car Price Prediction System

## 📌 Project Overview

This project is a complete end-to-end Machine Learning system that predicts the selling price of second-hand cars in India. The system uses historical car listing data from CarDekho, applies data preprocessing and feature engineering, trains multiple machine learning models, selects the best-performing model, explains predictions using SHAP Explainable AI, and serves predictions through a FastAPI backend, React frontend, SQLite database, Docker containers, and cloud deployment.

The final model achieved an **R² Score of 0.7987 (~80%)** using **CatBoost Regressor**.

---

# 🎯 Problem Statement

The used-car market often lacks transparent pricing. Buyers and sellers depend on dealer quotations, personal judgment, or online estimates.

This project aims to:

* Predict a fair selling price for used cars.
* Provide explainable predictions.
* Offer a user-friendly web and mobile interface.
* Maintain prediction history and analytics.

---

# 📊 Dataset Information

**Dataset Source:** CarDekho Used Car Dataset

### Original Dataset

| Property        | Value         |
| --------------- | ------------- |
| Records         | 4340          |
| Features        | 8             |
| Target Variable | selling_price |

### Original Features

* name
* year
* selling_price
* km_driven
* fuel
* seller_type
* transmission
* owner

---

# 🔍 Exploratory Data Analysis (EDA)

Performed:

* Missing value analysis
* Duplicate detection
* Outlier analysis
* Distribution analysis
* Correlation analysis
* Brand analysis
* Price distribution visualization

### Key Findings

* 763 duplicate rows detected and removed
* No missing values
* Significant outliers in selling_price and km_driven
* Vehicle age strongly impacts price

---

# ⚙️ Data Preprocessing & Feature Engineering

## Data Cleaning

* Removed duplicate records
* Handled outliers using 99th percentile capping
* Reduced brand cardinality

## Feature Engineering

### car_age

```python
car_age = 2024 - year
```

### km_per_year

```python
km_per_year = km_driven / (car_age + 1)
```

### brand_tier

Grouped brands into:

* Budget
* Mid-range
* Premium
* Luxury

## Encoding

### One-Hot Encoding

Applied to:

* fuel
* seller_type
* transmission
* owner
* brand_tier

### Label Encoding

Applied to:

* brand

## Feature Scaling

Used StandardScaler for:

* km_driven
* car_age
* km_per_year

---

# ⚠️ Data Leakage Fix

Initially, a feature called:

```python
depreciation_rate = selling_price / (car_age + 1)
```

was created.

This introduced data leakage because it directly used the target variable.

The feature was removed before final training.

---

# 🤖 Machine Learning Models Evaluated

| Model             | R² Score   |
| ----------------- | ---------- |
| Linear Regression | ~0.67      |
| Decision Tree     | ~0.67      |
| Random Forest     | ~0.78      |
| XGBoost           | ~0.79      |
| LightGBM          | ~0.79      |
| CatBoost          | **0.7987** |

---

# 🏆 Final Model

## CatBoost Regressor

### Performance Metrics

| Metric   | Value    |
| -------- | -------- |
| R² Score | 0.7987   |
| RMSE     | ₹184,805 |
| MAE      | ₹124,337 |
| CV R²    | ~0.79    |

### Why CatBoost?

* Highest R² score
* Lowest prediction error
* Excellent performance on tabular data
* Stable cross-validation results

---

# 🔎 Explainable AI (SHAP)

SHAP (SHapley Additive exPlanations) was integrated to make predictions transparent.

### Global Feature Importance

Top Influential Features:

1. Vehicle Age (car_age)
2. Luxury Brand Tier
3. Manual Transmission
4. Diesel Fuel Type
5. Premium Brand Tier

### Local Explainability

For every prediction, SHAP explains:

* Which features increased price
* Which features decreased price
* Contribution of each feature in rupees

---

# 🚀 FastAPI Backend

### Features

* Model Loading
* Prediction API
* Explainability API
* Prediction History
* Analytics
* Feedback Collection

### API Endpoints

#### General

* GET /
* GET /health

#### Model

* GET /model-info
* GET /feature-importance

#### Prediction

* POST /predict
* POST /predict-with-explanation

#### Analytics

* GET /predictions/history
* GET /predictions/stats

#### Feedback

* POST /feedback

---

# 🗄 Database Layer

Database: SQLite

### Tables

#### predictions

Stores:

* Input car details
* Predicted price
* Model used
* Device type
* Timestamp

#### feedback

Stores:

* Actual price
* User rating
* Comments

---

# 🎨 Frontend

Technology:

* React
* Tailwind CSS
* Recharts
* Axios
* Framer Motion

Features:

* Prediction Form
* SHAP Waterfall Charts
* Analytics Dashboard
* Prediction History
* Mobile Responsive Design

---

# 📱 Mobile Support

The application is fully mobile responsive and accessible through:

* Android
* iPhone
* Tablets

A Flutter mobile application was also integrated for mobile deployment.

---

# 🐳 Docker Deployment

### Backend Container

* Python 3.11
* FastAPI
* CatBoost Model

### Frontend Container

* React
* Nginx

### Docker Compose

Runs:

* Backend
* Frontend

with a single command:

```bash
docker-compose up --build
```

---

# ☁️ Cloud Deployment

### Backend

Render Deployment

### Frontend

Render / Vercel Deployment

### Benefits

* Public Access
* Automatic Deployment
* Cloud Hosting

---

# 🏗 System Architecture

User

↓

React Frontend / Flutter App

↓

FastAPI Backend

↓

CatBoost Model

↓

SHAP Explainer

↓

SQLite Database

---

# 📁 Project Structure

```text
CarPricePrediction/
│
├── backend/
├── frontend/
├── models/
├── notebooks/
├── dashboard/
├── docker-compose.yml
├── README.md
└── DEPLOYMENT.md
```

---

# 🔮 Future Improvements

* PostgreSQL Database
* User Authentication
* More Vehicle Features
* Real-time Market Data
* Advanced Hyperparameter Optimization
* Confidence Intervals
* Multi-Country Pricing Support

---

# 👨‍💻 Author

Durga Prasad S

B.E. Computer Science Engineering

PES University

---

# 📜 License

This project is developed for educational and academic purposes.
