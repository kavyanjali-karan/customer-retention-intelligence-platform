def test_amount_non_negative(transactions):
    assert (transactions["amount"] >= 0).all()

def test_amount_positive_sum(transactions):
    assert transactions["amount"].sum() > 0

def test_120k_transactions(transactions):
    assert len(transactions) >= 120000

def test_all_customers_have_revenue(transactions, customers):
    tx_customers = set(transactions["customer_id"].unique())
    all_customers = set(customers["customer_id"].unique())
    assert len(tx_customers & all_customers) / len(all_customers) > 0.95