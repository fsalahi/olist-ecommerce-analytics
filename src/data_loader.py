"""Load the Olist raw tables into pandas DataFrames."""
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

DATE_COLS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"],
}


def load_table(name: str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Load one table by short name, parsing its date columns."""
    path = raw_dir / FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. See docs/data_sources.md.")
    return pd.read_csv(path, parse_dates=DATE_COLS.get(name, []))


def load_all(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """Load every table into a dict keyed by short name."""
    return {name: load_table(name, raw_dir) for name in FILES}