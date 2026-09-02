import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def extract_data(file_path):
    df = pd.read_csv(file_path)
    return df

def clean_sales_data(df):
    clean_df = df.copy()
    clean_df["quantity"] = clean_df["quantity"].fillna(1)
    clean_df["order_date"] = pd.to_datetime(clean_df["order_date"])
    clean_df["total_sales"] = clean_df["price"] * clean_df["quantity"]
    return clean_df

def validate_data(df):
    duplicate_orders = df.duplicated(
        subset=["order_id"]
    ).sum()

    invalid_values = (
        (df["quantity"] <= 0) |
        (df["price"] <= 0)
    ).sum()

    missing_values = df[
        ["order_id", "product", "price", "order_date"]
    ].isna().sum().sum()

    if invalid_values > 0:
        raise ValueError("Invalid quantity or price detected")

    if duplicate_orders > 0:
        raise ValueError("Duplicate order IDs detected")

    if missing_values > 0:
        raise ValueError("Missing required values detected")

    return {
        "duplicate_orders": duplicate_orders,
        "invalid_values": invalid_values,
        "missing_values": missing_values
    }

def load_data(df, file_path):
    df.to_csv(file_path, index=False)

def run_pipeline(input_path, output_path):
    logging.info("Starting pipeline")

    logging.info("Extracting data")
    raw_df = extract_data(input_path)

    logging.info("Validating data")
    validate_data(raw_df)

    logging.info("Cleaning data")
    clean_df = clean_sales_data(raw_df)

    logging.info("Loading data")
    load_data(clean_df, output_path)

    logging.info("Pipeline completed")

    return clean_df