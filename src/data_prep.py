"""Build the order-level analytical table from the raw Olist tables."""
import pandas as pd

# Columns that are only known AFTER the order is placed. Use for EDA, never as model inputs.
LEAKAGE_COLS = [
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "delivery_days",
    "review_score",
]


def build_order_table(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # 1. Keep delivered orders that have a real delivery date
    orders = dfs["orders"]
    orders = orders[
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].notna()
    ].copy()

    # 2. Target and timing columns
    day = pd.Timedelta(days=1)
    orders["delivery_days"] = (
        orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
    ) / day
    orders["estimated_days"] = (
        orders["order_estimated_delivery_date"] - orders["order_purchase_timestamp"]
    ) / day
    orders["is_late"] = (
        orders["order_delivered_customer_date"] > orders["order_estimated_delivery_date"]
    ).astype(int)

    # 3. Purchase-time features
    ts = orders["order_purchase_timestamp"]
    orders["purchase_year"] = ts.dt.year
    orders["purchase_month"] = ts.dt.month
    orders["purchase_dayofweek"] = ts.dt.dayofweek
    orders["purchase_hour"] = ts.dt.hour

    # 4. Item-level enrichment: products, sellers, English category names
    products = dfs["products"].copy()
    products["product_volume_cm3"] = (
        products["product_length_cm"]
        * products["product_height_cm"]
        * products["product_width_cm"]
    )
    items = (
        dfs["order_items"]
        .merge(
            products[["product_id", "product_category_name",
                      "product_weight_g", "product_volume_cm3"]],
            on="product_id", how="left",
        )
        .merge(dfs["sellers"][["seller_id", "seller_state"]], on="seller_id", how="left")
        .merge(dfs["category_translation"], on="product_category_name", how="left")
    )

    # 5. Aggregate items to one row per order
    items_agg = items.groupby("order_id").agg(
        n_items=("order_item_id", "count"),
        n_products=("product_id", "nunique"),
        n_sellers=("seller_id", "nunique"),
        total_price=("price", "sum"),
        total_freight=("freight_value", "sum"),
        total_weight_g=("product_weight_g", "sum"),
        total_volume_cm3=("product_volume_cm3", "sum"),
    ).reset_index()

    # Category and seller state of the order's most expensive item
    primary = (
        items.sort_values("price", ascending=False)
        .drop_duplicates("order_id")[["order_id", "product_category_name_english", "seller_state"]]
        .rename(columns={"product_category_name_english": "main_category"})
    )

    # 6. Payments to one row per order
    pay = dfs["payments"]
    pay_agg = pay.groupby("order_id").agg(
        total_payment=("payment_value", "sum"),
        max_installments=("payment_installments", "max"),
        n_payment_methods=("payment_type", "nunique"),
    ).reset_index()
    main_pay = (
        pay.sort_values("payment_value", ascending=False)
        .drop_duplicates("order_id")[["order_id", "payment_type"]]
        .rename(columns={"payment_type": "main_payment_type"})
    )

    # 7. Reviews to one row per order (EDA only: known after delivery)
    reviews = dfs["reviews"].groupby("order_id")["review_score"].mean().reset_index()

    # 8. Customers (customer_id is unique per order)
    customers = dfs["customers"][
        ["customer_id", "customer_unique_id", "customer_state",
         "customer_city", "customer_zip_code_prefix"]
    ]

    # 9. Join everything onto orders (left joins keep every delivered order)
    n_before = len(orders)
    master = (
        orders.merge(items_agg, on="order_id", how="left")
        .merge(primary, on="order_id", how="left")
        .merge(pay_agg, on="order_id", how="left")
        .merge(main_pay, on="order_id", how="left")
        .merge(reviews, on="order_id", how="left")
        .merge(customers, on="customer_id", how="left")
    )
    assert len(master) == n_before, "Join changed the row count: a key is not unique"

    # 10. Cleaning: drop orders with no items, label unknown categories
    master = master[master["n_items"].notna()].copy()
    master["main_category"] = master["main_category"].fillna("unknown")

    return master.reset_index(drop=True)

def time_split(master: pd.DataFrame, test_size: float = 0.2):
    """Chronological split: the most recent `test_size` share of orders becomes the test set."""
    ordered = master.sort_values("order_purchase_timestamp")
    cutoff = ordered["order_purchase_timestamp"].iloc[int(len(ordered) * (1 - test_size))]
    train = ordered[ordered["order_purchase_timestamp"] < cutoff]
    test = ordered[ordered["order_purchase_timestamp"] >= cutoff]
    return train.reset_index(drop=True), test.reset_index(drop=True)