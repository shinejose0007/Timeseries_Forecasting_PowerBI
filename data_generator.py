"""Generate synthetic SKU-level daily time series data for a pharma/chemical-like use case."""
import numpy as np, pandas as pd, yaml, os
from datetime import timedelta, date

def load_config(path='example_config.yaml'):
    with open(path) as f:
        return yaml.safe_load(f)

def make_date_range(days, end_date=None):
    if end_date is None:
        end_date = pd.Timestamp.today().normalize()
    start = end_date - pd.Timedelta(days=days-1)
    return pd.date_range(start, end_date, freq='D')

def generate_sku_series(sku_id, dates, seed=0):
    rng = np.random.RandomState(seed+sku_id)
    n = len(dates)
    # baseline + small trend
    baseline = rng.uniform(50, 500)
    trend = np.linspace(0, rng.uniform(-0.2, 1.0) * n/365, n)
    # weekly & yearly seasonality
    weekly = 10 * np.sin(2 * np.pi * dates.dayofweek / 7 + rng.rand()*2*np.pi)
    yearly = 30 * np.sin(2 * np.pi * dates.dayofyear / 365 + rng.rand()*2*np.pi)
    # promotion spikes (randomly placed)
    promo = np.zeros(n)
    for _ in range(rng.randint(2,6)):
        loc = rng.randint(0, n)
        width = rng.randint(3, 15)
        mag = rng.uniform(0.2, 1.5) * baseline
        idx = slice(max(0, loc-width), min(n, loc+width))
        promo[idx] += mag * np.exp(-np.linspace(0,2, idx.stop-idx.start))
    noise = rng.normal(0, baseline * 0.08, n)
    qty = baseline + trend + weekly + yearly + promo + noise
    qty = np.maximum(0, qty).round(0)
    df = pd.DataFrame({'date': dates, 'sku': f'SKU_{sku_id:04d}', 'demand': qty.astype(int)})
    # add metadata
    df['plant'] = f'Plant_{(sku_id%5)+1}'
    df['category'] = f'Cat_{(sku_id%8)+1}'
    return df

def generate_all(output_csv='data/synthetic_sku_daily.csv', config_path='example_config.yaml'):
    cfg = load_config(config_path)
    dates = make_date_range(cfg.get('days', 1095))
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    parts = []
    for sku in range(1, cfg.get('num_skus',50)+1):
        parts.append(generate_sku_series(sku, dates, seed=cfg.get('random_seed',42)))
    df = pd.concat(parts, ignore_index=True)
    df.to_csv(output_csv, index=False)
    print(f"Generated {len(df):,} rows -> {output_csv}")
    return df

if __name__ == '__main__':
    generate_all()
