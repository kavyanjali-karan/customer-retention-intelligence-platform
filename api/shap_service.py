import pickle
import shap
import pandas as pd

with open("artifacts/shap_explainer.pkl", "rb") as f:
    explainer = pickle.load(f)

def explain_customer(df):

    shap_values = explainer(df)

    values = shap_values.values[0]

    feature_names = df.columns

    feature_imp = pd.DataFrame({
        "feature": feature_names,
        "impact": values
    })

    feature_imp["abs"] = feature_imp["impact"].abs()

    feature_imp = feature_imp.sort_values(
        "abs",
        ascending=False
    )

    top3 = feature_imp.head(3)

    return top3[["feature","impact"]]