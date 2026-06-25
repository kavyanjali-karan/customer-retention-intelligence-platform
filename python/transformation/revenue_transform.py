import pandas as pd


def transform_revenue(df):

    df["revenue"]=df["revenue"].round(2)

    return df