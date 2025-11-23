# Time-series Forecasting Project (Pharma/Chemical example)

This repository contains a ready-to-run example of a time-series forecasting pipeline using synthetic data, XGBoost-based forecasting, and a Streamlit app to run batch forecasts and export CSV/Excel files for Power BI or MySQL ingestion.

**Contents**
- `data_generator.py` — synthesize SKU-level daily timeseries (trend, seasonality, noise, promotions).
- `feature_engineering.py` — create lag & rolling features for XGBoost.
- `model_train.py` — trains per-SKU XGBoost models and saves forecasts.
- `batch_forecast.py` — runs forecasts for all SKUs and outputs (1) SKU-level daily forecasts CSV and (2) aggregated monthly CSV.
- `streamlit_app.py` — a Streamlit UI to run batch forecasts and download produced CSVs; optional MySQL upload.
- `export_mysql.py` — example script to load CSVs into a MySQL table using SQLAlchemy.
- `powerbi_instructions.md` — step-by-step to import CSV/Excel and MySQL in Power BI, suggested visuals & Power Query snippets.
- `requirements.txt` — required Python packages.
- `example_config.yaml` — adjustable parameters (num_skus, days, forecast_horizon, output sizes).

Default settings generate ~50 SKUs × 3 years daily data (~54k rows). Change `example_config.yaml` for larger outputs (increase `num_skus` or `days`).

---
