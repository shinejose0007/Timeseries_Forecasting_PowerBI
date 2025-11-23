"""Streamlit app to run batch forecasts, show simple visuals, and export CSVs or push to MySQL."""

import streamlit as st, pandas as pd, os, subprocess, yaml
from pathlib import Path

st.set_page_config(page_title='TS Forecast Demo', layout='wide')

st.title('Time-series Forecasting')

st.sidebar.header('Runner')
if 'cfg' not in st.session_state:
    st.session_state['cfg'] = yaml.safe_load(open('example_config.yaml'))

cfg = st.session_state['cfg']

st.sidebar.number_input('Number of SKUs', min_value=1, max_value=2000, value=cfg.get('num_skus',50), key='num_skus')
st.sidebar.number_input('Days (history)', min_value=90, max_value=3650, value=cfg.get('days',1095), key='days')
st.sidebar.number_input('Forecast horizon (days)', min_value=7, max_value=365, value=cfg.get('forecast_horizon',90), key='horizon')

if st.sidebar.button('Run full batch pipeline'):
    # update example_config.yaml
    new_cfg = {'num_skus': int(st.session_state['num_skus']), 'days': int(st.session_state['days']), 'forecast_horizon': int(st.session_state['horizon']), 'random_seed':42}
    with open('example_config.yaml','w') as f:
        yaml.safe_dump(new_cfg, f)
    st.info('Config updated — running batch pipeline (this runs local scripts).')
    # Run batch_forecast.py
    with st.spinner('Running batch pipeline...'):
        os.system('python3 batch_forecast.py')
    st.success('Done — outputs written to /outputs')

st.header('Download outputs')
if Path('outputs/sku_forecasts_daily.csv').exists():
    st.write('SKU-level daily forecasts')
    st.download_button('Download SKU-level CSV', data=open('outputs/sku_forecasts_daily.csv','rb').read(), file_name='sku_forecasts_daily.csv')
if Path('outputs/agg_monthly_forecast.csv').exists():
    st.write('Aggregated monthly forecast')
    st.download_button('Download monthly CSV', data=open('outputs/agg_monthly_forecast.csv','rb').read(), file_name='agg_monthly_forecast.csv')

st.sidebar.header('MySQL Upload (optional)')
upload_to_mysql = st.sidebar.checkbox('Enable MySQL upload')
if upload_to_mysql:
    mysql_host = st.sidebar.text_input('Host', value='localhost')
    mysql_port = st.sidebar.text_input('Port', value='3306')
    mysql_db = st.sidebar.text_input('Database', value='forecast_db')
    mysql_user = st.sidebar.text_input('User', value='root')
    mysql_pass = st.sidebar.text_input('Password', value='', type='password')
    if st.sidebar.button('Upload CSVs to MySQL'):
        st.info('Uploading...')
        cmd = f"python3 export_mysql.py --host {mysql_host} --port {mysql_port} --db {mysql_db} --user {mysql_user} --password '{mysql_pass}'"
        os.system(cmd)
        st.success('Upload finished. Check logs in console.')

st.markdown('''
### Notes
- This is a demo pipeline. For production consider model registry, hyperparameter tuning, better iterative forecast logic (e.g. use covariates), and monitoring.
- Increase `num_skus` in `example_config.yaml` to generate larger outputs. Keep an eye on runtime and memory.
''')
