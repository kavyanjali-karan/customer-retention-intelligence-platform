import pandas as pd


def export(df,path):

    df.to_excel(

        path,

        index=False

    )