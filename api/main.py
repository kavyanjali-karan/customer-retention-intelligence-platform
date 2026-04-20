"""
Churn Autopsy — FastAPI Inference API
POST /predict  → churn probability + top-3 SHAP reasons per customer
GET  /health   → model metadata
GET  /docs     → auto-generated Swagger UI (built into FastAPI)

Run: uvicorn api.main:app --reload --port 8000
"""

import os
import joblib
import shap
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, List

# ── Load model artefacts ─────────────────────────────────────────────────────
BASE       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE, 'models', 'churn_pipeline.pkl')

try:
    artefacts     = joblib.load(MODEL_PATH)
    pipeline      = artefacts['pipeline']
    preprocessor  = artefacts['preprocessor']
    feature_names = artefacts['feature_names']
    cat_cols      = artefacts['cat_cols']
    num_cols      = artefacts['num_cols']
    metrics       = artefacts['metrics']
    clf           = pipeline.named_steps['clf']
    MODEL_LOADED  = True
except Exception as e:
    MODEL_LOADED  = False
    LOAD_ERROR    = str(e)

app = FastAPI(
    title="Churn Autopsy API",
    description="Predicts telecom customer churn probability and explains the top drivers per customer using SHAP.",
    version="1.0.0",
)

# ── Request / Response schemas ────────────────────────────────────────────────
class CustomerInput(BaseModel):
    gender:           Literal['Male', 'Female']                          = Field(..., example='Female')
    SeniorCitizen:    Literal[0, 1]                                      = Field(..., example=0)
    Partner:          Literal['Yes', 'No']                               = Field(..., example='Yes')
    Dependents:       Literal['Yes', 'No']                               = Field(..., example='No')
    tenure:           int                                                 = Field(..., ge=0, le=72, example=5)
    PhoneService:     Literal['Yes', 'No']                               = Field(..., example='Yes')
    MultipleLines:    Literal['Yes', 'No', 'No phone service']           = Field(..., example='No')
    InternetService:  Literal['DSL', 'Fiber optic', 'No']               = Field(..., example='Fiber optic')
    OnlineSecurity:   Literal['Yes', 'No', 'No internet service']        = Field(..., example='No')
    OnlineBackup:     Literal['Yes', 'No', 'No internet service']        = Field(..., example='No')
    DeviceProtection: Literal['Yes', 'No', 'No internet service']        = Field(..., example='No')
    TechSupport:      Literal['Yes', 'No', 'No internet service']        = Field(..., example='No')
    StreamingTV:      Literal['Yes', 'No', 'No internet service']        = Field(..., example='No')
    StreamingMovies:  Literal['Yes', 'No', 'No internet service']        = Field(..., example='No')
    Contract:         Literal['Month-to-month', 'One year', 'Two year']  = Field(..., example='Month-to-month')
    PaperlessBilling: Literal['Yes', 'No']                               = Field(..., example='Yes')
    PaymentMethod:    Literal[
        'Electronic check', 'Mailed check',
        'Bank transfer (automatic)', 'Credit card (automatic)'
    ]                                                                     = Field(..., example='Electronic check')
    MonthlyCharges:   float                                               = Field(..., ge=0, example=70.35)
    TotalCharges:     float                                               = Field(..., ge=0, example=351.75)


class ShapReason(BaseModel):
    feature:    str
    value:      str
    impact:     str
    shap_value: float


class PredictionResponse(BaseModel):
    churn_probability: float
    churn_prediction:  str
    risk_level:        str
    top_3_reasons:     List[ShapReason]
    retention_action:  str
    model_roc_auc:     float


# ── Helper: build feature DataFrame ──────────────────────────────────────────
def build_features(customer: CustomerInput) -> pd.DataFrame:
    d  = customer.model_dump()
    df = pd.DataFrame([d])

    df['tenure_bucket'] = pd.cut(
        df['tenure'], bins=[0, 12, 24, 48, 72],
        labels=['0-12m', '13-24m', '25-48m', '49-72m'],
        include_lowest=True
    )
    df['has_streaming'] = (
        (df['StreamingTV'] == 'Yes') | (df['StreamingMovies'] == 'Yes')
    ).astype(int)
    df['has_protection'] = (
        (df['OnlineSecurity'] == 'Yes') |
        (df['OnlineBackup']   == 'Yes') |
        (df['DeviceProtection'] == 'Yes')
    ).astype(int)
    df['charge_per_tenure'] = df['MonthlyCharges'] / (df['tenure'] + 1)

    return df[cat_cols + num_cols]


# ── Helper: retention recommendation ─────────────────────────────────────────
def retention_action(prob: float, top_reasons: list) -> str:
    feature_str = ' '.join([r['feature'].lower() for r in top_reasons])
    if prob < 0.30:
        return "Low risk — standard engagement. No immediate intervention required."
    elif prob < 0.55:
        if 'contract' in feature_str:
            return "Moderate risk — offer a discounted annual contract upgrade to lock in tenure."
        elif 'fiber' in feature_str or 'internet' in feature_str:
            return "Moderate risk — proactively check service quality; offer a tech support call."
        else:
            return "Moderate risk — personalised check-in call recommended within 30 days."
    else:
        if 'contract' in feature_str:
            return "High risk — immediate intervention: offer 2-month free contract extension or loyalty discount."
        elif 'security' in feature_str or 'protection' in feature_str:
            return "High risk — bundle OnlineSecurity + DeviceProtection at reduced rate; highlight value."
        elif 'tenure' in feature_str:
            return "High risk — early-tenure customer; assign dedicated onboarding support rep."
        else:
            return "High risk — escalate to retention team within 48 hours."


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail=f"Model not loaded: {LOAD_ERROR}")
    return {
        "status":  "healthy",
        "model":   metrics['best_model'],
        "roc_auc": metrics['roc_auc'],
        "pr_auc":  metrics['pr_auc'],
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerInput):
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Model not loaded. Run src/train.py first.")

    X    = build_features(customer)
    prob = float(pipeline.predict_proba(X)[0][1])
    prediction = "Churn" if prob >= 0.5 else "Stay"
    risk = "High" if prob >= 0.55 else ("Moderate" if prob >= 0.30 else "Low")

    # SHAP explanation for this specific customer
    X_transformed = preprocessor.transform(X)

    try:
        from sklearn.linear_model import LogisticRegression as LR
        if isinstance(clf, LR):
            explainer = shap.LinearExplainer(clf, X_transformed)
            sv        = explainer.shap_values(X_transformed)[0]
        else:
            explainer = shap.TreeExplainer(clf)
            sv_raw    = explainer.shap_values(X_transformed)
            sv        = sv_raw[1][0] if isinstance(sv_raw, list) else sv_raw[0]

        shap_pairs = sorted(
            zip(feature_names, sv, X_transformed[0]),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        top_reasons = []
        for feat, shap_val, raw_val in shap_pairs[:3]:
            top_reasons.append(ShapReason(
                feature    = feat,
                value      = str(round(float(raw_val), 3)),
                impact     = "increases churn risk" if shap_val > 0 else "decreases churn risk",
                shap_value = round(float(shap_val), 4)
            ))
    except Exception:
        top_reasons = []

    action = retention_action(prob, [r.model_dump() for r in top_reasons])

    return PredictionResponse(
        churn_probability = round(prob, 4),
        churn_prediction  = prediction,
        risk_level        = risk,
        top_3_reasons     = top_reasons,
        retention_action  = action,
        model_roc_auc     = metrics['roc_auc'],
    )