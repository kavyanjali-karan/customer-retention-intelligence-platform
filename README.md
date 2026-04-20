# 🔬 Churn Autopsy
### *Why customers leave — predicted before they do*

An end-to-end ML system that predicts telecom customer churn **and explains exactly why** — per customer, not just globally. Built as a production-style pipeline: trained model → REST API → interactive dashboard.

---

## 🎯 The Problem

Telecom companies lose 15–25% of customers annually to churn. Retaining an existing customer costs 5–7x less than acquiring a new one. The challenge isn't just predicting *who* will churn — it's understanding *why*, fast enough to intervene.

This project solves both.

---

## 🏗️ Architecture
data/telco_churn.csv
│
▼
src/train.py            ← Training pipeline
├── Feature engineering (4 derived features)
├── Preprocessing (OHE + StandardScaler + Imputer)
├── SMOTE oversampling (class imbalance handling)
├── Model comparison (LR vs RF vs GBM, 5-fold CV)
├── SHAP global feature importance
└── Joblib export → models/churn_pipeline.pkl
│
▼
api/main.py             ← FastAPI inference layer
├── POST /predict     → churn probability + top-3 SHAP reasons
└── GET  /health      → model metadata
│
▼
app.py                  ← Streamlit UI
├── Customer input form
├── Risk banner (High / Moderate / Low)
├── SHAP reason cards (per-customer explanation)
└── Retention action recommendation
---

## 📊 Model Performance

| Metric           | Score  |
|-----------------|--------|
| ROC-AUC         | 0.744  |
| PR-AUC          | 0.564  |
| Churn Recall    | 0.66   |
| Churn Precision | 0.52   |

> **Why precision-recall, not accuracy?** The dataset has ~33% churn. A model predicting "never churn" gets 67% accuracy while being completely useless. PR-AUC is the honest metric for imbalanced classification.

---

## 🧠 Top Churn Drivers (SHAP)

| Rank | Feature | Direction |
|------|---------|-----------|
| 1 | Month-to-month contract | ⬆️ Increases risk |
| 2 | Two-year contract | ⬇️ Decreases risk |
| 3 | Tenure 49–72 months | ⬇️ Decreases risk |
| 4 | Fiber optic internet | ⬆️ Increases risk |
| 5 | Electronic check payment | ⬆️ Increases risk |

---

## 🚀 Run Locally

```bash
# 1. Clone and install
git clone https://github.com/karankavyanjali77-sys/churn-autopsy
cd churn-autopsy
pip install -r requirements.txt

# 2. Generate data
cd data && python generate_data.py && cd ..

# 3. Train the model
python src/train.py

# 4. Start the API — Terminal 1
uvicorn api.main:app --reload --port 8000

# 5. Start the dashboard — Terminal 2
streamlit run app.py
```

- Dashboard: `http://localhost:8501`
- API docs: `http://localhost:8000/docs`

---

## 🔌 API Example

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Female", "SeniorCitizen": 0,
    "Partner": "Yes", "Dependents": "No", "tenure": 5,
    "PhoneService": "Yes", "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No", "OnlineBackup": "No",
    "DeviceProtection": "No", "TechSupport": "No",
    "StreamingTV": "No", "StreamingMovies": "No",
    "Contract": "Month-to-month", "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 70.35, "TotalCharges": 351.75
  }'
```

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Data & EDA | Pandas, NumPy, Seaborn, Matplotlib |
| ML Pipeline | Scikit-learn, Imbalanced-learn (SMOTE) |
| Explainability | SHAP |
| Model Persistence | Joblib |
| API | FastAPI, Pydantic, Uvicorn |
| Dashboard | Streamlit |

---

## 📁 Project Structure
churn-autopsy/
├── data/
│   ├── generate_data.py
│   └── telco_churn.csv
├── models/
│   └── churn_pipeline.pkl      (auto-generated)
├── src/
│   └── train.py
├── api/
│   ├── init.py
│   └── main.py
├── notebooks/
│   ├── evaluation_plots.png    (auto-generated)
│   └── shap_importance.png     (auto-generated)
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
---

## 👩‍💻 Author

**Kavyanjali Karan** · B.Tech CSE, ITER SOA University
[LinkedIn](https://linkedin.com/in/kavyanjali-karan) · [GitHub](https://github.com/karankavyanjali77-sys)