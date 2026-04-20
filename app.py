"""
Churn Autopsy — Streamlit Dashboard
Calls the FastAPI /predict endpoint and renders results visually.

Run BOTH at the same time:
  Terminal 1: uvicorn api.main:app --port 8000
  Terminal 2: streamlit run app.py
"""

import streamlit as st
import requests

API_URL = "http://localhost:8000"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Churn Autopsy",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title  { font-size:2.4rem; font-weight:800; color:#1a1a2e; margin-bottom:4px; }
    .sub-title   { font-size:1rem; color:#555; margin-bottom:24px; }
    .risk-high   { background:#fde8e8; border-left:5px solid #c0392b; padding:16px; border-radius:6px; }
    .risk-mod    { background:#fef9e7; border-left:5px solid #f39c12; padding:16px; border-radius:6px; }
    .risk-low    { background:#eafaf1; border-left:5px solid #27ae60; padding:16px; border-radius:6px; }
    .reason-card { background:#f8f9fa; border-radius:8px; padding:12px 16px; margin:6px 0; border:1px solid #e0e0e0; }
    .metric-box  { text-align:center; padding:16px; border-radius:8px; background:#f0f4ff; }
    .action-box  { background:#1a56a0; color:white; padding:16px; border-radius:8px; margin-top:12px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🔬 Churn Autopsy</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Why customers leave — predicted before they do.</div>', unsafe_allow_html=True)

# ── API health check ──────────────────────────────────────────────────────────
try:
    health = requests.get(f"{API_URL}/health", timeout=3).json()
    st.sidebar.success(f"✅ API connected\nModel: {health['model']}\nROC-AUC: {health['roc_auc']}")
except Exception:
    st.sidebar.error("❌ API offline.\nRun in a separate terminal:\nuvicorn api.main:app --port 8000")

# ── Sidebar — Customer Input ──────────────────────────────────────────────────
st.sidebar.header("Customer Profile")
st.sidebar.markdown("---")

with st.sidebar:
    st.subheader("Demographics")
    gender     = st.selectbox("Gender",          ["Male", "Female"])
    senior     = st.selectbox("Senior Citizen",  [0, 1], format_func=lambda x: "Yes" if x else "No")
    partner    = st.selectbox("Partner",         ["Yes", "No"])
    dependents = st.selectbox("Dependents",      ["Yes", "No"])
    tenure     = st.slider("Tenure (months)",    0, 72, 5)

    st.subheader("Services")
    phone_svc  = st.selectbox("Phone Service",   ["Yes", "No"])
    multi_lines= st.selectbox("Multiple Lines",  ["No", "Yes", "No phone service"])
    internet   = st.selectbox("Internet Service",["Fiber optic", "DSL", "No"])
    online_sec = st.selectbox("Online Security", ["No", "Yes", "No internet service"])
    online_bkp = st.selectbox("Online Backup",   ["No", "Yes", "No internet service"])
    dev_prot   = st.selectbox("Device Protection",["No", "Yes", "No internet service"])
    tech_sup   = st.selectbox("Tech Support",    ["No", "Yes", "No internet service"])
    stream_tv  = st.selectbox("Streaming TV",    ["No", "Yes", "No internet service"])
    stream_mov = st.selectbox("Streaming Movies",["No", "Yes", "No internet service"])

    st.subheader("Billing")
    contract   = st.selectbox("Contract",        ["Month-to-month", "One year", "Two year"])
    paperless  = st.selectbox("Paperless Billing",["Yes", "No"])
    payment    = st.selectbox("Payment Method",  [
        "Electronic check", "Mailed check",
        "Bank transfer (automatic)", "Credit card (automatic)"
    ])
    monthly_chg = st.number_input("Monthly Charges ($)", 18.0, 120.0, 70.35, step=0.5)
    total_chg   = st.number_input("Total Charges ($)",   0.0,  9000.0,
                                  float(monthly_chg * tenure), step=1.0)

    predict_btn = st.button("🔬 Run Autopsy", use_container_width=True, type="primary")

# ── Main Panel ────────────────────────────────────────────────────────────────
if predict_btn:
    payload = {
        "gender": gender, "SeniorCitizen": senior,
        "Partner": partner, "Dependents": dependents, "tenure": tenure,
        "PhoneService": phone_svc, "MultipleLines": multi_lines,
        "InternetService": internet, "OnlineSecurity": online_sec,
        "OnlineBackup": online_bkp, "DeviceProtection": dev_prot,
        "TechSupport": tech_sup, "StreamingTV": stream_tv,
        "StreamingMovies": stream_mov, "Contract": contract,
        "PaperlessBilling": paperless, "PaymentMethod": payment,
        "MonthlyCharges": monthly_chg, "TotalCharges": total_chg,
    }

    with st.spinner("Running prediction..."):
        try:
            resp = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
            if resp.status_code != 200:
                st.error(f"API error {resp.status_code}: {resp.text}")
                st.stop()
            result = resp.json()
        except Exception as e:
            st.error(f"Could not connect to API: {e}\n\nMake sure this is running in another terminal:\nuvicorn api.main:app --port 8000")
            st.stop()

    prob       = result["churn_probability"]
    risk       = result["risk_level"]
    prediction = result["churn_prediction"]
    reasons    = result["top_3_reasons"]
    action     = result["retention_action"]
    pct        = int(prob * 100)

    # Risk banner
    risk_class = {"High": "risk-high", "Moderate": "risk-mod", "Low": "risk-low"}[risk]
    emoji      = {"High": "🔴", "Moderate": "🟡", "Low": "🟢"}[risk]

    st.markdown(f"""
    <div class="{risk_class}">
        <h2 style="margin:0">{emoji} {risk} Churn Risk — {pct}% probability of leaving</h2>
        <p style="margin:4px 0 0 0; font-size:0.95rem;">
            Prediction: <strong>{prediction}</strong> &nbsp;|&nbsp;
            Model ROC-AUC: <strong>{result['model_roc_auc']}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Churn Probability")
        st.progress(prob)
        st.markdown(
            f"<div class='metric-box'><h1>{pct}%</h1><p>Likelihood of churning</p></div>",
            unsafe_allow_html=True
        )

    with col2:
        st.subheader("🧠 Top 3 Reasons (SHAP)")
        if reasons:
            for i, r in enumerate(reasons, 1):
                direction = "⬆️ Increases" if "increases" in r["impact"] else "⬇️ Decreases"
                shap_abs  = abs(r["shap_value"])
                bar       = "█" * int(shap_abs * 10) + "░" * max(0, 10 - int(shap_abs * 10))
                st.markdown(f"""
                <div class="reason-card">
                    <strong>#{i} {r['feature']}</strong><br>
                    <small>Value: {r['value']} &nbsp;|&nbsp; {direction} risk</small><br>
                    <code style="font-size:0.8rem">{bar} {shap_abs:.3f}</code>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("SHAP explanations unavailable for this prediction.")

    st.markdown("---")
    st.subheader("💡 Recommended Retention Action")
    st.markdown(
        f'<div class="action-box"><strong>{action}</strong></div>',
        unsafe_allow_html=True
    )

    with st.expander("📋 Raw API Response (JSON)"):
        st.json(result)

else:
    st.info("👈 Fill in the customer profile in the sidebar and click **Run Autopsy**.")

    st.markdown("### How it works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**1. Input**\nEnter customer demographics, services, and billing details in the sidebar.")
    with col2:
        st.markdown("**2. Predict**\nA trained classifier returns the churn probability via a FastAPI REST endpoint.")
    with col3:
        st.markdown("**3. Explain**\nSHAP values identify the top 3 features driving this specific customer's risk.")

    st.markdown("---")
    st.markdown("**Dataset:** IBM Telco Customer Churn — 7,043 customers, 21 features")
    st.markdown("**Techniques:** SMOTE · OneHotEncoding · StandardScaler · SHAP · FastAPI · Streamlit")