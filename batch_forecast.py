"""
Wrapper to run full pipeline and create aggregated outputs and metrics.

Usage: python batch_forecast.py
"""
import os
from data_generator import generate_all
from model_train import train_and_forecast
import pandas as pd

def run_all(config_path='example_config.yaml'):
    # Step A: generate synthetic data
    print('Generating data...')
    generate_all(output_csv='data/synthetic_sku_daily.csv', config_path=config_path)

    # Step B: train models, forecast, and compute metrics
    print('Training models and forecasting... (this may take a while)')
    forecasts, metrics = train_and_forecast(input_csv='data/synthetic_sku_daily.csv')

    # Step C: create aggregated outputs
    if forecasts is None or forecasts.empty:
        print('No forecasts produced.')
        return False

    forecasts['date'] = pd.to_datetime(forecasts['date'])
    forecasts.to_csv('outputs/sku_forecasts_daily.csv', index=False)

    # Monthly aggregation
    sku_monthly = forecasts.copy()
    sku_monthly['month'] = sku_monthly['date'].dt.to_period('M').dt.to_timestamp()
    agg_monthly = sku_monthly.groupby(['month']).agg(total_forecast=('forecast','sum')).reset_index()
    agg_monthly.to_csv('outputs/agg_monthly_forecast.csv', index=False)
    print('Aggregated monthly forecast written -> outputs/agg_monthly_forecast.csv')

    # Save metrics
    if metrics is not None and not metrics.empty:
        metrics.to_csv('outputs/forecast_metrics.csv', index=False)
        print('Metrics written -> outputs/forecast_metrics.csv')

    print('All done.')
    return True

if __name__ == '__main__':
    run_all()
