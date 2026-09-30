def test_customer_unique(customers):
    assert customers["customer_id"].duplicated().sum() == 0

def test_no_null_ids(customers):
    assert customers["customer_id"].isnull().sum() == 0

def test_15k_customers(customers):
    assert len(customers) == 15000

def test_valid_segments(customers):
    valid = {"Enterprise", "MidMarket", "SMB"}
    assert set(customers["segment"].unique()).issubset(valid)