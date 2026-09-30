"""Shared fixtures for customer retention tests."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
import pandas as pd

DATA_DIR = ROOT / "data" / "raw"

RAW_FILES = ["customers.csv", "revenue_transactions.csv", "customer_activity.csv"]


def _ensure_data() -> None:
    """Build the (gitignored, seeded) datasets on a fresh clone."""
    if all((DATA_DIR / name).exists() for name in RAW_FILES):
        return
    subprocess.run(
        [sys.executable, str(ROOT / "data" / "generate_data.py")],
        check=True,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


_ensure_data()


@pytest.fixture(scope="session")
def customers():
    return pd.read_csv(DATA_DIR / "customers.csv")


@pytest.fixture(scope="session")
def transactions():
    return pd.read_csv(DATA_DIR / "revenue_transactions.csv")
