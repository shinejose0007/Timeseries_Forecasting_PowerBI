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


# Quick start

1. Create a Python environment and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

3. Or run the pipeline directly:

```bash
python data_generator.py
python model_train.py
python batch_forecast.py
```


# Power BI - Step by step using the generated outputs

## Option A: Import CSV/Excel
1. Open Power BI Desktop -> Get Data -> Text/CSV. Choose `outputs/sku_forecasts_daily.csv`.
2. In Power Query: change `date` column type to Date.
3. Create relationships if you also import `data/synthetic_sku_daily.csv` (join by `sku` + `date`).
4. Suggested visuals:
   - Line chart: `date` on X, `forecast` on Y, small multiples by `sku` (or use slicer to choose SKU)
   - Matrix: `sku` rows, `month` columns, aggregated sum of forecast
   - Card + KPI: total forecast this month, comparison vs previous month
5. Use Power Query to create `month` column: `Date.StartOfMonth([date])` or M: `Date.StartOfMonth([date])`.

## Option B: Connect to MySQL
1. Get Data -> MySQL database. Provide host, database, and credentials.
2. Choose the `sku_forecasts_daily` and `agg_monthly_forecast` tables.
3. Build visuals as above. Use DirectQuery if you want near-real-time (be mindful of performance).

## Power Query tips / transformations
- To pivot monthly data for a heatmap: Group By `sku` and `month` -> Sum `forecast` -> Pivot `month`.
- For large row counts, prefer aggregated tables (monthly or weekly) and push-heavy operations to the database.

## Suggested PBIX layout
- Page 1: Overview (totals, KPI, trend line)
- Page 2: SKU Explorer (slicer for SKU, line chart with actual vs forecast)
- Page 3: Plant / Category analysis (bar charts)


Outputs appear in `outputs/` (CSV files). Use Power BI to import those CSVs or upload them to MySQL via `export_mysql.py`.
<p align="center">
  <img src="Test3.JPG" width="1000">
</p


<p align="center">
  <img src="Test4.JPG" width="1000">
</p


<p align="center">
  <img src="Test2.JPG" width="1000">
</p


<p align="center">
  <img src="Test1.JPG" width="1000">
</p

---
