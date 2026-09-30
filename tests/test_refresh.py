def test_customers_exist():
    import pandas as pd
    from pathlib import Path
    df = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "raw" / "customers.csv")
    assert len(df) > 0

def test_transactions_exist():
    import pandas as pd
    from pathlib import Path
    df = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "raw" / "revenue_transactions.csv")
    assert len(df) >= 120000