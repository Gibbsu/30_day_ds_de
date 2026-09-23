import pandas as pd
import pytest
import duckdb
from src.config import PIPELINE_ENV, PROJECT_ROOT
from src.pipeline import (
    clean_sales_data,validate_data,
    run_pipeline,
    load_incremental_orders,
    run_transaction_safe_load)

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

def test_pipeline_environment():
    assert PIPELINE_ENV == "development"

def test_pipeline_output():
    input_path = PROJECT_ROOT / "data/day_06_pipeline_output.csv"
    output_path = PROJECT_ROOT / "data/day_13_pipeline_output.csv"

    result_df = run_pipeline(input_path,output_path)

    assert output_path.exists()
    assert "total_sales" in result_df.columns

def test_incremental_load():
    test_df = pd.DataFrame({"order_id":[1,2,3],
                            "product":["Laptop","Monitor","Keyboard"],
                            "quantity":[1,2,1],
                            "price":[1200,300,100],
                            "order_date":["2026-01-01","2026-01-02","2026-01-03"]})
    clean_test_df = clean_sales_data(test_df)
    con = duckdb.connect(":memory:")
    load_incremental_orders(clean_test_df,con)
    load_incremental_orders(clean_test_df,con)
    row_count = con.execute("""
        SELECT
            COUNT(*)
        FROM clean_orders""").fetchone()[0]
    assert row_count == 3
    con.close()

def test_transaction_safe_load():
    con = duckdb.connect(":memory:")
    test_df = pd.DataFrame({"order_id":[3001],
                  "product":['Keyboard'],
                  "quantity":[2],
                  "price":[75],
                  "order_date":['2026-03-01']})
    clean_test_df = clean_sales_data(test_df)
    run_transaction_safe_load(clean_test_df, con)
    row_count = con.execute("""
        SELECT
            COUNT(*)
        FROM clean_orders
    """).fetchone()[0]
    assert row_count == 1
    run_transaction_safe_load(clean_test_df, con)
    repeat_row_count = con.execute("""
        SELECT
            COUNT(*)
        FROM clean_orders
    """).fetchone()[0]
    assert repeat_row_count == 1
    con.close()

def test_transaction_rollback():
    con = duckdb.connect(":memory:")
    test_df = pd.DataFrame({"order_id":[4001],
                            "product":['Mouse'],
                            "quantity":[2],
                            "price":[50],
                            "order_date":['2026-03-02']})
    clean_test_df = clean_sales_data(test_df)
    empty_test_df = clean_test_df.head(0)
    load_incremental_orders(empty_test_df, con)
    con.execute('BEGIN')
    load_incremental_orders(clean_test_df, con)
    con.execute('ROLLBACK')
    row_count = con.execute("""
            SELECT
                COUNT(*)
            FROM clean_orders
        """).fetchone()[0]
    assert row_count == 0
    con.close()