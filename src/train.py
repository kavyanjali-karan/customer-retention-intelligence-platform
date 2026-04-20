"""
Churn Autopsy — Training Pipeline
Trains a Random Forest classifier on the IBM Telco churn dataset.
Handles class imbalance with SMOTE, evaluates with precision/recall/ROC-AUC,
generates SHAP explainability, and exports the model pipeline via Joblib.

To run: python src/train.py
"""

import os
import warnings
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import shap

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_curve, roc_curve, average_precision_score
)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

warnings.filterwarnings('ignore')

# ── Paths ────────────────────────────────────────────────────────────────────
BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA  = os.path.join(BASE, 'data', 'telco_churn.csv')
MDIR  = os.path.join(BASE, 'models')
NDIR  = os.path.join(BASE, 'notebooks')
os.makedirs(MDIR, exist_ok=True)
os.makedirs(NDIR, exist_ok=True)

# ── 1. Load & Clean ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("CHURN AUTOPSY — TRAINING PIPELINE")
print("="*60)

df = pd.read_csv(DATA)
print(f"\n[1] Loaded {len(df):,} rows, {df.shape[1]} columns")

# Drop customerID — not a feature
df.drop(columns=['customerID'], inplace=True)

# TotalCharges: 11 blanks → coerce to float, fill with median
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'].fillna(df['TotalCharges'].median(), inplace=True)

# Target
df['Churn'] = (df['Churn'] == 'Yes').astype(int)
churn_rate = df['Churn'].mean()
print(f"    Churn rate: {churn_rate:.1%}  (class imbalance present — SMOTE will be applied)")

# ── 2. Feature Engineering ───────────────────────────────────────────────────
print("\n[2] Feature engineering...")

# Tenure buckets (useful for SHAP readability)
df['tenure_bucket'] = pd.cut(df['tenure'],
    bins=[0, 12, 24, 48, 72],
    labels=['0-12m', '13-24m', '25-48m', '49-72m'],
    include_lowest=True
)

# Has any streaming service
df['has_streaming'] = (
    (df['StreamingTV'] == 'Yes') | (df['StreamingMovies'] == 'Yes')
).astype(int)

# Has any protection service
df['has_protection'] = (
    (df['OnlineSecurity'] == 'Yes') |
    (df['OnlineBackup'] == 'Yes') |
    (df['DeviceProtection'] == 'Yes')
).astype(int)

# Charges per month of tenure (avoid division by zero)
df['charge_per_tenure'] = df['MonthlyCharges'] / (df['tenure'] + 1)

print(f"    Added 4 engineered features: tenure_bucket, has_streaming, has_protection, charge_per_tenure")

# ── 3. Train / Test Split ────────────────────────────────────────────────────
CAT_COLS = [
    'gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
    'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
    'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
    'PaperlessBilling', 'PaymentMethod', 'tenure_bucket'
]
NUM_COLS = [
    'SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges',
    'has_streaming', 'has_protection', 'charge_per_tenure'
]

X = df[CAT_COLS + NUM_COLS]
y = df['Churn']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n[3] Split: {len(X_train):,} train / {len(X_test):,} test (stratified)")

# ── 4. Preprocessing ─────────────────────────────────────────────────────────
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CAT_COLS),
    ('num', Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler',  StandardScaler()),
    ]), NUM_COLS),
])

# ── 5. Model Comparison ──────────────────────────────────────────────────────
print("\n[4] Comparing models (5-fold stratified CV on ROC-AUC)...")

candidates = {
    'Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
    'Random Forest':       RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42, n_jobs=-1),
    'Gradient Boosting':   GradientBoostingClassifier(n_estimators=200, random_state=42),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results = {}

for name, clf in candidates.items():
    pipe = Pipeline([('pre', preprocessor), ('clf', clf)])
    scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring='roc_auc', n_jobs=-1)
    results[name] = scores
    print(f"    {name:25s}  ROC-AUC: {scores.mean():.4f} ± {scores.std():.4f}")

best_name = max(results, key=lambda k: results[k].mean())
print(f"\n    → Best model: {best_name}")

# ── 6. Final Pipeline with SMOTE ─────────────────────────────────────────────
print(f"\n[5] Training final {best_name} pipeline with SMOTE...")

best_clf = candidates[best_name]

final_pipeline = ImbPipeline([
    ('pre',   preprocessor),
    ('smote', SMOTE(random_state=42, k_neighbors=5)),
    ('clf',   best_clf),
])

final_pipeline.fit(X_train, y_train)
print("    Training complete.")

# ── 7. Evaluation ─────────────────────────────────────────────────────────────
print("\n[6] Evaluation on held-out test set...")

y_pred      = final_pipeline.predict(X_test)
y_prob      = final_pipeline.predict_proba(X_test)[:, 1]
roc_auc     = roc_auc_score(y_test, y_prob)
avg_prec    = average_precision_score(y_test, y_prob)

print(f"\n    ROC-AUC : {roc_auc:.4f}")
print(f"    Avg Precision (PR-AUC): {avg_prec:.4f}")
print(f"\n    Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=['Stay', 'Churn']))

# ── 8. Save plots ─────────────────────────────────────────────────────────────
print("\n[7] Generating evaluation plots...")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Churn Autopsy — Model Evaluation", fontsize=14, fontweight='bold')

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0],
            xticklabels=['Stay','Churn'], yticklabels=['Stay','Churn'])
axes[0].set_title('Confusion Matrix')
axes[0].set_ylabel('Actual'); axes[0].set_xlabel('Predicted')

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
axes[1].plot(fpr, tpr, color='#1a56a0', lw=2, label=f'ROC-AUC = {roc_auc:.3f}')
axes[1].plot([0,1],[0,1], 'k--', lw=1)
axes[1].set_title('ROC Curve'); axes[1].set_xlabel('FPR'); axes[1].set_ylabel('TPR')
axes[1].legend(); axes[1].grid(alpha=0.3)

# Precision-Recall Curve
prec, rec, _ = precision_recall_curve(y_test, y_prob)
axes[2].plot(rec, prec, color='#e05c1a', lw=2, label=f'PR-AUC = {avg_prec:.3f}')
axes[2].set_title('Precision-Recall Curve')
axes[2].set_xlabel('Recall'); axes[2].set_ylabel('Precision')
axes[2].legend(); axes[2].grid(alpha=0.3)

plt.tight_layout()
plot_path = os.path.join(NDIR, 'evaluation_plots.png')
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"    Saved: {plot_path}")

# ── 9. SHAP Feature Importance ────────────────────────────────────────────────
print("\n[8] Computing SHAP values (global feature importance)...")

pre_step  = final_pipeline.named_steps['pre']
clf_step  = final_pipeline.named_steps['clf']

X_test_transformed = pre_step.transform(X_test)

cat_feature_names = pre_step.named_transformers_['cat'].get_feature_names_out(CAT_COLS).tolist()
all_feature_names = cat_feature_names + NUM_COLS

# Use TreeExplainer for RF/GB, LinearExplainer for LR
if isinstance(clf_step, LogisticRegression):
    explainer  = shap.LinearExplainer(clf_step, X_test_transformed)
    shap_vals  = explainer.shap_values(X_test_transformed)
else:
    explainer  = shap.TreeExplainer(clf_step)
    shap_out   = explainer.shap_values(X_test_transformed)
    shap_vals  = shap_out[1] if isinstance(shap_out, list) else shap_out

# Global bar plot — top 15 features
shap_df = pd.DataFrame(np.abs(shap_vals), columns=all_feature_names)
top_features = shap_df.mean().sort_values(ascending=False).head(15)

fig, ax = plt.subplots(figsize=(10, 6))
top_features[::-1].plot(kind='barh', color='#1a56a0', ax=ax)
ax.set_title('SHAP Feature Importance — Top 15 Churn Drivers', fontweight='bold')
ax.set_xlabel('Mean |SHAP value|')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
shap_path = os.path.join(NDIR, 'shap_importance.png')
plt.savefig(shap_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"    Saved: {shap_path}")
print(f"\n    Top 5 churn drivers:")
for feat, val in top_features.head(5).items():
    print(f"      {feat:45s}  {val:.4f}")

# ── 10. Export model artefacts ────────────────────────────────────────────────
print("\n[9] Exporting model artefacts...")

artefacts = {
    'pipeline':      final_pipeline,
    'preprocessor':  pre_step,
    'feature_names': all_feature_names,
    'cat_cols':      CAT_COLS,
    'num_cols':      NUM_COLS,
    'metrics': {
        'roc_auc':   round(roc_auc, 4),
        'pr_auc':    round(avg_prec, 4),
        'best_model': best_name,
    }
}

model_path = os.path.join(MDIR, 'churn_pipeline.pkl')
joblib.dump(artefacts, model_path)
print(f"    Saved: {model_path}  ({os.path.getsize(model_path)/1024:.1f} KB)")

print("\n" + "="*60)
print("TRAINING COMPLETE")
print(f"  Model : {best_name}")
print(f"  ROC-AUC : {roc_auc:.4f}")
print(f"  PR-AUC  : {avg_prec:.4f}")
print("="*60 + "\n")