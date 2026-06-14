import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─── Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Car Price Predictor",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Endpoint
API_URL = "http://localhost:8000"

# Constants
VALID_BRANDS = [
    "Audi", "Chevrolet", "Fiat", "Ford", "Honda", "Hyundai",
    "Mahindra", "Maruti", "Nissan", "Other", "Renault", "Skoda",
    "Tata", "Toyota", "Volkswagen",
]
VALID_FUELS = ["Petrol", "Diesel", "CNG", "LPG", "Electric"]
VALID_SELLER_TYPES = ["Individual", "Dealer", "Trustmark Dealer"]
VALID_TRANSMISSIONS = ["Manual", "Automatic"]
VALID_OWNERS = [
    "First Owner", "Second Owner", "Third Owner",
    "Fourth & Above Owner", "Test Drive Car",
]

# ─── Sidebar: User Inputs ────────────────────────────────────────────────
st.sidebar.header("🚗 Enter Car Details")

brand = st.sidebar.selectbox("Brand", VALID_BRANDS, index=VALID_BRANDS.index("Maruti"))
year = st.sidebar.number_input("Manufacture Year", min_value=1990, max_value=2024, value=2015, step=1)
km_driven = st.sidebar.number_input("Kilometers Driven", min_value=0, value=50000, step=1000)
fuel = st.sidebar.selectbox("Fuel Type", VALID_FUELS, index=VALID_FUELS.index("Petrol"))
seller_type = st.sidebar.selectbox("Seller Type", VALID_SELLER_TYPES, index=VALID_SELLER_TYPES.index("Individual"))
transmission = st.sidebar.selectbox("Transmission", VALID_TRANSMISSIONS, index=VALID_TRANSMISSIONS.index("Manual"))
owner = st.sidebar.selectbox("Owner", VALID_OWNERS, index=VALID_OWNERS.index("First Owner"))

st.sidebar.markdown("---")
show_explanation = st.sidebar.checkbox("Include SHAP Explanation", value=True)

predict_btn = st.sidebar.button("🔮 Predict Price", type="primary", use_container_width=True)

# ─── Main View ──────────────────────────────────────────────────────────
st.title("Second-Hand Car Price Predictor")
st.markdown("Predict the selling price of a used car in India using a trained CatBoost model.")

# Health check
@st.cache_data(ttl=60)
def check_api_health():
    try:
        res = requests.get(f"{API_URL}/health", timeout=2)
        if res.status_code == 200:
            return True, res.json()
        return False, None
    except Exception:
        return False, None

is_api_healthy, health_data = check_api_health()
if not is_api_healthy:
    st.error(f"⚠️ Cannot connect to the Prediction API at `{API_URL}`. Make sure the FastAPI server is running.")
    st.stop()

# Information Tabs
tab1, tab2 = st.tabs(["Prediction", "Model Info"])

with tab2:
    st.subheader("Model Information")
    try:
        info_res = requests.get(f"{API_URL}/model-info").json()
        col1, col2, col3 = st.columns(3)
        col1.metric("Model Used", info_res["model_name"])
        col2.metric("R² Score", f"{info_res['r2_score']:.4f}")
        col3.metric("RMSE", f"₹ {info_res['rmse']:,.0f}")
        st.json(info_res)
    except Exception as e:
        st.warning(f"Could not load model info: {e}")

    st.subheader("Global Feature Importance")
    try:
        fi_res = requests.get(f"{API_URL}/feature-importance").json()
        fi_df = pd.DataFrame(fi_res)
        fig = px.bar(
            fi_df, 
            x='importance', 
            y='feature', 
            orientation='h',
            title='Top Features by Importance',
            color='importance',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load feature importance: {e}")

with tab1:
    if predict_btn:
        payload = {
            "brand": brand,
            "year": year,
            "km_driven": km_driven,
            "fuel": fuel,
            "seller_type": seller_type,
            "transmission": transmission,
            "owner": owner
        }

        with st.spinner("Analyzing car details..."):
            endpoint = "/predict-with-explanation" if show_explanation else "/predict"
            try:
                response = requests.post(f"{API_URL}{endpoint}", json=payload)
                response.raise_for_status()
                data = response.json()

                st.success("Prediction successful!")
                
                # Display Prediction
                st.markdown("### Estimated Selling Price")
                st.markdown(f"<h1 style='text-align: center; color: #2e8b57;'>₹ {data['predicted_price']:,.0f}</h1>", unsafe_allow_html=True)
                
                # Show Explanation
                if show_explanation and "top_factors" in data:
                    st.markdown("---")
                    st.subheader("Why this price?")
                    st.info(data["explanation_text"])
                    
                    st.markdown("### Top Price Factors")
                    factors = data["top_factors"]
                    
                    # Create Waterfall-like chart for SHAP
                    # We start from base_value and add each shap_value
                    features = [f["feature"] for f in factors]
                    shap_values = [f["shap_value"] for f in factors]
                    
                    # For Waterfall chart, we need Base -> Features -> Final (Prediction)
                    # Note: Top 5 factors might not sum exactly to predicted_price due to other missing factors
                    # So we calculate the "Other factors" difference
                    top_factors_sum = sum(shap_values)
                    base_val = data["base_value"]
                    pred_val = data["predicted_price"]
                    other_val = pred_val - (base_val + top_factors_sum)
                    
                    x_labels = ["Base Price"] + features + ["Other Factors", "Predicted Price"]
                    y_values = [base_val] + shap_values + [other_val, pred_val]
                    measure = ["absolute"] + ["relative"] * len(features) + ["relative", "total"]
                    
                    fig_waterfall = go.Figure(go.Waterfall(
                        name="SHAP Explanation",
                        orientation="v",
                        measure=measure,
                        x=x_labels,
                        textposition="outside",
                        text=[f"₹{v:,.0f}" if i==0 or i==len(y_values)-1 else f"{'+' if v>0 else ''}₹{v:,.0f}" for i, v in enumerate(y_values)],
                        y=y_values,
                        connector={"line": {"color": "rgb(63, 63, 63)"}},
                    ))
                    
                    fig_waterfall.update_layout(
                        title="Price Breakdown (SHAP Values)",
                        showlegend=False,
                        waterfallgap=0.3
                    )
                    st.plotly_chart(fig_waterfall, use_container_width=True)

            except requests.exceptions.RequestException as e:
                st.error(f"Error communicating with API: {e}")
                if response is not None:
                    st.error(f"API Details: {response.text}")
    else:
        st.info("👈 Enter the car details in the sidebar and click **Predict Price**.")
