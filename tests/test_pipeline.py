import pandas as pd
import pytest

from src.pipeline import clean_sales_data,validate_data

def test_clean_sales_data():
    df = pd.DataFrame({
        "order_id": [1],
        "product": ["Laptop"],
        "quantity": [None],
        "price": [1200],
        "order_date": ["2026-01-01"]
    })
    result = clean_sales_data(df)
    assert result.loc[0, "quantity"] == 1

def test_validate_data_duplicate_orders():
    df = pd.DataFrame({
            "order_id": [1,1],
            "product": ["Laptop","Monitor"],
            "quantity": [1,2],
            "price": [1200, 300],
            "order_date": ["2026-01-01", "2026-01-02"]
        })
    with pytest.raises(ValueError,match="Duplicate order IDs detected"):
        validate_data(df)