def test_revenue(df):

    assert df["revenue"].sum()>=0