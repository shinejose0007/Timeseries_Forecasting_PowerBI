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

4. Outputs appear in `outputs/` (CSV files). Use Power BI to import those CSVs or upload them to MySQL via `export_mysql.py`.
