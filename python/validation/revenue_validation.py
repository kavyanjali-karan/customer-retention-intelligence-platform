def validate_revenue(df):

    assert (df["revenue"]>=0).all()

    return True