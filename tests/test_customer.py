def test_customer(df):

    assert df["customer_id"].duplicated().sum()==0