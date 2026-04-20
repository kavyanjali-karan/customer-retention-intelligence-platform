import pandas as pd
import numpy as np

np.random.seed(42)
n = 7043

gender = np.random.choice(['Male','Female'], n)
senior = np.random.choice([0,1], n, p=[0.84,0.16])
partner = np.random.choice(['Yes','No'], n, p=[0.48,0.52])
dependents = np.random.choice(['Yes','No'], n, p=[0.30,0.70])
tenure = np.random.randint(0, 73, n)
phone = np.random.choice(['Yes','No'], n, p=[0.90,0.10])
multiple_lines = np.where(phone=='No', 'No phone service',
                 np.random.choice(['Yes','No'], n, p=[0.53,0.47]))
internet = np.random.choice(['DSL','Fiber optic','No'], n, p=[0.34,0.44,0.22])

def inet_svc(p=0.5):
    return np.where(internet=='No', 'No internet service',
           np.random.choice(['Yes','No'], n, p=[p, 1-p]))

online_security  = inet_svc(0.29)
online_backup    = inet_svc(0.34)
device_protect   = inet_svc(0.34)
tech_support     = inet_svc(0.29)
streaming_tv     = inet_svc(0.38)
streaming_movies = inet_svc(0.39)
contract = np.random.choice(['Month-to-month','One year','Two year'], n, p=[0.55,0.21,0.24])
paperless = np.random.choice(['Yes','No'], n, p=[0.59,0.41])
payment = np.random.choice(
    ['Electronic check','Mailed check','Bank transfer (automatic)','Credit card (automatic)'],
    n, p=[0.34,0.23,0.22,0.21])
monthly_charges = np.round(np.random.uniform(18, 119, n), 2)
total_charges = np.round(monthly_charges * tenure + np.random.normal(0,50,n), 2)
total_charges = np.clip(total_charges, 0, None)

churn_prob = (
    0.05
    + 0.30 * (contract == 'Month-to-month')
    + 0.15 * (internet == 'Fiber optic')
    + 0.10 * (online_security == 'No')
    + 0.08 * (tenure < 12)
    - 0.10 * (tenure > 48)
    - 0.08 * (contract == 'Two year')
    + 0.05 * (payment == 'Electronic check')
    + 0.03 * (senior == 1)
)
churn_prob = np.clip(churn_prob, 0.02, 0.95)
churn = np.where(np.random.random(n) < churn_prob, 'Yes', 'No')

ids = []
for _ in range(n):
    ids.append(f'{np.random.randint(1000,9999)}-{"".join(np.random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 5))}')

df = pd.DataFrame({
    'customerID': ids, 'gender': gender, 'SeniorCitizen': senior,
    'Partner': partner, 'Dependents': dependents, 'tenure': tenure,
    'PhoneService': phone, 'MultipleLines': multiple_lines,
    'InternetService': internet, 'OnlineSecurity': online_security,
    'OnlineBackup': online_backup, 'DeviceProtection': device_protect,
    'TechSupport': tech_support, 'StreamingTV': streaming_tv,
    'StreamingMovies': streaming_movies, 'Contract': contract,
    'PaperlessBilling': paperless, 'PaymentMethod': payment,
    'MonthlyCharges': monthly_charges, 'TotalCharges': total_charges,
    'Churn': churn
})

mask = np.random.choice(df.index, 11, replace=False)
df.loc[mask, 'TotalCharges'] = None

df.to_csv('telco_churn.csv', index=False)
print(f"Done. Rows: {len(df)}, Churn rate: {(df['Churn']=='Yes').mean():.1%}")