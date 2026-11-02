# Data Sources

**Dataset:** Brazilian E-Commerce Public Dataset by Olist
**Link:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
**License:** see the Kaggle page

## How to obtain
1. Download the zip from Kaggle.
2. Extract the 9 CSV files into `data/raw/`.

## Tables
| Table | Description |
|---|---|
| orders | One row per order, with status and timestamps |
| order_items | Products within each order, with price and freight |
| payments | Payment method and value per order |
| reviews | Customer review scores and comments |
| customers | Customer location (customer_id is per order; customer_unique_id is per person) |
| sellers | Seller location |
| products | Product attributes and category |
| geolocation | Zip code prefix to latitude/longitude |
| category_translation | Portuguese to English category names |