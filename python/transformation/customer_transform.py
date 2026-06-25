import pandas as pd


def transform_customer(df):

    df.columns=df.columns.str.lower()

    df["customer_id"]=df["customer_id"].str.strip()

    df["customer_segment"]=df["customer_segment"].str.upper()

    return df