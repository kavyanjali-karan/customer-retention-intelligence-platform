"""
Churn Autopsy — Standalone Streamlit App
Loads the trained model directly — no FastAPI needed.
Deploy to Streamlit Cloud: streamlit run app.py
"""

import os
import joblib
import shap
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Churn Autopsy", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")

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
    .info-box    { background:#f0f4ff; border-left:4px solid #1a56a0; padding:12px 16px; border-radius:6px; margin:8px 0; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'churn_pipeline.pkl')
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)

artefacts = load_model()

CAT_COLS = [
    'gender','Partner','Dependents','PhoneService','MultipleLines',
    'InternetService','OnlineSecurity','OnlineBackup','DeviceProtection',
    'TechSupport','StreamingTV','StreamingMovies','Contract',
    'PaperlessBilling','PaymentMethod','tenure_bucket'
]
NUM_COLS = [
    'SeniorCitizen','tenure','MonthlyCharges','TotalCharges',
    'has_streaming','has_protection','charge_per_tenure'
]

def build_features(inputs):
    df = pd.DataFrame([inputs])
    df['tenure_bucket'] = pd.cut(df['tenure'], bins=[0,12,24,48,72],
        labels=['0-12m','13-24m','25-48m','49-72m'], include_lowest=True)
    df['has_streaming']  = ((df['StreamingTV']=='Yes')|(df['StreamingMovies']=='Yes')).astype(int)
    df['has_protection'] = ((df['OnlineSecurity']=='Yes')|(df['OnlineBackup']=='Yes')|(df['DeviceProtection']=='Yes')).astype(int)
    df['charge_per_tenure'] = df['MonthlyCharges'] / (df['tenure'] + 1)
    return df[CAT_COLS + NUM_COLS]

def get_shap_reasons(clf, feature_names, X_transformed):
    try:
        from sklearn.linear_model import LogisticRegression as LR
        if isinstance(clf, LR):
            shap_vals = clf.coef_[0] * X_transformed[0]
        else:
            explainer = shap.TreeExplainer(clf)
            sv_raw    = explainer.shap_values(X_transformed)
            shap_vals = sv_raw[1][0] if isinstance(sv_raw, list) else sv_raw[0]
        pairs = sorted(zip(feature_names, shap_vals, X_transformed[0]), key=lambda x: abs(x[1]), reverse=True)
        return [(f, float(sv), float(rv)) for f, sv, rv in pairs[:3]]
    except Exception:
        return []

def retention_action(prob, reasons):
    fs = ' '.join([r[0].lower() for r in reasons])
    if prob < 0.30:
        return "Low risk — standard engagement. No immediate intervention required."
    elif prob < 0.55:
        if 'contract' in fs: return "Moderate risk — offer a discounted annual contract upgrade to lock in tenure."
        elif 'fiber' in fs or 'internet' in fs: return "Moderate risk — proactively check service quality; offer a tech support call."
        else: return "Moderate risk — personalised check-in call recommended within 30 days."
    else:
        if 'contract' in fs: return "High risk — immediate intervention: offer 2-month free contract extension or loyalty discount."
        elif 'security' in fs or 'protection' in fs: return "High risk — bundle OnlineSecurity + DeviceProtection at reduced rate; highlight value."
        elif 'tenure' in fs: return "High risk — early-tenure customer; assign dedicated onboarding support rep."
        else: return "High risk — escalate to retention team within 48 hours."

st.markdown('<div class="main-title">🔬 Churn Autopsy</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Why customers leave — predicted before they do.</div>', unsafe_allow_html=True)

if artefacts is None:
    st.sidebar.error("❌ Model not found. Run src/train.py first.")
    st.stop()

metrics = artefacts['metrics']
st.sidebar.success(f"✅ Model loaded\n**{metrics['best_model']}**\nROC-AUC: {metrics['roc_auc']}  |  PR-AUC: {metrics['pr_auc']}")
st.sidebar.header("Customer Profile")
st.sidebar.markdown("---")

with st.sidebar:
    st.subheader("Demographics")
    gender     = st.selectbox("Gender",            ["Male","Female"])
    senior     = st.selectbox("Senior Citizen",    [0,1], format_func=lambda x: "Yes" if x else "No")
    partner    = st.selectbox("Partner",           ["Yes","No"])
    dependents = st.selectbox("Dependents",        ["Yes","No"])
    tenure     = st.slider("Tenure (months)",      0, 72, 5)
    st.subheader("Services")
    phone_svc  = st.selectbox("Phone Service",     ["Yes","No"])
    multi_lines= st.selectbox("Multiple Lines",    ["No","Yes","No phone service"])
    internet   = st.selectbox("Internet Service",  ["Fiber optic","DSL","No"])
    online_sec = st.selectbox("Online Security",   ["No","Yes","No internet service"])
    online_bkp = st.selectbox("Online Backup",     ["No","Yes","No internet service"])
    dev_prot   = st.selectbox("Device Protection", ["No","Yes","No internet service"])
    tech_sup   = st.selectbox("Tech Support",      ["No","Yes","No internet service"])
    stream_tv  = st.selectbox("Streaming TV",      ["No","Yes","No internet service"])
    stream_mov = st.selectbox("Streaming Movies",  ["No","Yes","No internet service"])
    st.subheader("Billing")
    contract   = st.selectbox("Contract",          ["Month-to-month","One year","Two year"])
    paperless  = st.selectbox("Paperless Billing", ["Yes","No"])
    payment    = st.selectbox("Payment Method",    ["Electronic check","Mailed check","Bank transfer (automatic)","Credit card (automatic)"])
    monthly_chg = st.number_input("Monthly Charges ($)", 18.0, 120.0, 70.35, step=0.5)
    total_chg   = st.number_input("Total Charges ($)",   0.0,  9000.0, float(monthly_chg * tenure), step=1.0)
    predict_btn = st.button("🔬 Run Autopsy", use_container_width=True, type="primary")

if predict_btn:
    inputs = {
        "gender":gender,"SeniorCitizen":senior,"Partner":partner,"Dependents":dependents,
        "tenure":tenure,"PhoneService":phone_svc,"MultipleLines":multi_lines,
        "InternetService":internet,"OnlineSecurity":online_sec,"OnlineBackup":online_bkp,
        "DeviceProtection":dev_prot,"TechSupport":tech_sup,"StreamingTV":stream_tv,
        "StreamingMovies":stream_mov,"Contract":contract,"PaperlessBilling":paperless,
        "PaymentMethod":payment,"MonthlyCharges":monthly_chg,"TotalCharges":total_chg,
    }
    with st.spinner("Running prediction..."):
        pipeline      = artefacts['pipeline']
        preprocessor  = artefacts['preprocessor']
        feature_names = artefacts['feature_names']
        clf           = pipeline.named_steps['clf']
        X             = build_features(inputs)
        prob          = float(pipeline.predict_proba(X)[0][1])
        prediction    = "Churn" if prob >= 0.5 else "Stay"
        risk          = "High" if prob >= 0.55 else ("Moderate" if prob >= 0.30 else "Low")
        pct           = int(prob * 100)
        X_transformed = preprocessor.transform(X)
        reasons       = get_shap_reasons(clf, feature_names, X_transformed)
        action        = retention_action(prob, reasons)

    risk_class = {"High":"risk-high","Moderate":"risk-mod","Low":"risk-low"}[risk]
    emoji      = {"High":"🔴","Moderate":"🟡","Low":"🟢"}[risk]
    st.markdown(f"""
    <div class="{risk_class}">
        <h2 style="margin:0">{emoji} {risk} Churn Risk — {pct}% probability of leaving</h2>
        <p style="margin:4px 0 0 0; font-size:0.95rem;">
            Prediction: <strong>{prediction}</strong> &nbsp;|&nbsp;
            Model: <strong>{metrics['best_model']}</strong> &nbsp;|&nbsp;
            ROC-AUC: <strong>{metrics['roc_auc']}</strong>
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Churn Probability")
        st.progress(prob)
        st.markdown(f"<div class='metric-box'><h1>{pct}%</h1><p>Likelihood of churning</p></div>", unsafe_allow_html=True)
    with col2:
        st.subheader("🧠 Top 3 Reasons (SHAP)")
        if reasons:
            for i,(feat,shap_val,raw_val) in enumerate(reasons,1):
                direction = "⬆️ Increases" if shap_val > 0 else "⬇️ Decreases"
                shap_abs  = abs(shap_val)
                filled    = int(min(shap_abs * 7, 10))
                bar       = "█"*filled + "░"*(10-filled)
                st.markdown(f"""
                <div class="reason-card">
                    <strong>#{i} {feat}</strong><br>
                    <small>Value: {round(raw_val,3)} &nbsp;|&nbsp; {direction} risk</small><br>
                    <code style="font-size:0.8rem">{bar} {shap_abs:.3f}</code>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("SHAP explanations unavailable for this prediction.")

    st.markdown("---")
    st.subheader("💡 Recommended Retention Action")
    st.markdown(f'<div class="action-box"><strong>{action}</strong></div>', unsafe_allow_html=True)

    with st.expander("📋 Full Prediction Details (JSON)"):
        st.json({
            "churn_probability": round(prob,4), "churn_prediction": prediction, "risk_level": risk,
            "top_3_reasons": [{"feature":f,"shap_value":round(sv,4),"impact":"increases churn risk" if sv>0 else "decreases churn risk"} for f,sv,_ in reasons],
            "retention_action": action, "model": metrics['best_model'], "roc_auc": metrics['roc_auc'],
        })

else:
    st.info("👈 Fill in the customer profile in the sidebar and click **Run Autopsy** to get a prediction.")
    st.markdown("### How it works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="info-box"><strong>1. Input</strong><br>Enter customer demographics, services, and billing details in the sidebar.</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="info-box"><strong>2. Predict</strong><br>A trained classifier selected via 5-fold CV returns the churn probability with SMOTE-balanced training.</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="info-box"><strong>3. Explain</strong><br>SHAP values identify the top 3 features driving <em>this specific customer\'s</em> risk — not global averages.</div>', unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dataset", "7,043 customers")
    col2.metric("ROC-AUC", metrics['roc_auc'])
    col3.metric("PR-AUC",  metrics['pr_auc'])
    col4.metric("Features", "21 raw + 4 engineered")
    st.markdown("---")
    st.markdown("**Stack:** Scikit-learn · SMOTE · SHAP · Joblib · Streamlit &nbsp;|&nbsp; **[View source on GitHub](https://github.com/karankavyanjali77-sys/churn-autopsy)**")