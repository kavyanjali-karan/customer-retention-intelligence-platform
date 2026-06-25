import numpy as np


def health_score(df):

    df["health_score"]=np.where(

        df["churn_probability"]>0.6,

        "High Risk",

        "Healthy"

    )

    return df