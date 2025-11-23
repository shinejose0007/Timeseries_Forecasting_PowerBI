"""Create lag and rolling features for tree-based time-series forecasting (XGBoost)."""
import pandas as pd, numpy as np

def create_features(df, lags=(1,7,14,28), rolling_windows=(7,14,28)):
    df = df.copy()
    df = df.sort_values(['sku','date'])
    for lag in lags:
        df[f'lag_{lag}'] = df.groupby('sku')['demand'].shift(lag)
    for w in rolling_windows:
        df[f'roll_mean_{w}'] = df.groupby('sku')['demand'].shift(1).rolling(window=w, min_periods=1).mean().reset_index(level=0, drop=True)
        df[f'roll_std_{w}'] = df.groupby('sku')['demand'].shift(1).rolling(window=w, min_periods=1).std().reset_index(level=0, drop=True).fillna(0)
    # date features
    df['dow'] = df['date'].dt.dayofweek
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['is_weekend'] = (df['dow']>=5).astype(int)
    return df

if __name__ == '__main__':
    print('Run feature engineering by importing create_features from this module.')
