# Olist E-Commerce Analytics

End-to-end analysis and machine learning on the Olist Brazilian e-commerce dataset.

## Project goals
- Explore order, customer, seller and delivery patterns
- Predict late deliveries / low review scores
- Translate findings into business recommendations

## Project structure
- `data/` – raw and processed data (not tracked; see setup: .gitignore)
- `notebooks/` – analysis notebooks
- `src/` – reusable code
- `reports/figures/` – exported charts
- `docs/` – supporting notes

## Setup
### In macOS
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

### In Windows
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip

## Dataset
Brazilian E-Commerce Public Dataset by Olist: 
kaggle.com/datasets/olistbr/brazilian-ecommerce
For more information, check out: docs/data_sources.md

## Status
Work in progress.