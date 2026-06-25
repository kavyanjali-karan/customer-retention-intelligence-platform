def validate_metrics(df):

    assert df["paid_customers"].sum()>=0

    assert df["churned_customers"].sum()>=0

    return True