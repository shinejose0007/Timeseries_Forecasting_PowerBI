"""
Train XGBoost per-SKU models and generate forecasts for a horizon.
Outputs:
 - models/<SKU>.joblib
 - outputs/sku_forecasts_daily.csv   (forecasts)
 - outputs/forecast_metrics.csv      (per-SKU RMSE/MAE/MAPE/sMAPE)
 - prediction intervals added as lower_q and upper_q columns (e.g. 10th/90th percentiles)

Notes:
 - Prediction intervals are computed using validation residual percentiles (residual-based approach).
"""
import os
import pandas as pd
import numpy as np
import joblib
import yaml
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
from feature_engineering import create_features


def load_config(path='example_config.yaml'):
    with open(path) as f:
        return yaml.safe_load(f)


def safe_mape(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mask = y_true != 0
    if mask.sum() == 0:
        return np.nan
    return (np.abs((y_true[mask] - y_pred[mask]) / y_true[mask]).mean()) * 100.0


def smape(a, f):
    a = np.array(a)
    f = np.array(f)
    denom = (np.abs(a) + np.abs(f))
    mask = denom != 0
    if mask.sum() == 0:
        return np.nan
    return (100.0 * (np.abs(a[mask] - f[mask]) / denom[mask]).mean())


def train_and_forecast(input_csv='data/synthetic_sku_daily.csv',
                       horizon=None,
                       models_dir='models',
                       out_forecast='outputs/sku_forecasts_daily.csv',
                       out_metrics='outputs/forecast_metrics.csv',
                       lower_q=0.10,
                       upper_q=0.90):
    """
    Train per-SKU XGBoost models and produce iterative forecasts + residual-based intervals.

    Returns:
      out_df: DataFrame of forecasts (sku, date, forecast, lower_q, upper_q)
      metrics_df: per-SKU metrics (rmse, mae, mape, smape)
    """
    cfg = load_config()
    horizon = cfg.get('forecast_horizon', horizon or 90)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(os.path.dirname(out_forecast), exist_ok=True)

    df = pd.read_csv(input_csv, parse_dates=['date'])
    df_feat = create_features(df)

    exclude = set(['date', 'sku', 'plant', 'category', 'demand'])
    features = [c for c in df_feat.columns if c not in exclude]

    results = []
    metrics = []
    skus = df_feat['sku'].unique()

    for sku in skus:
        sdf = df_feat[df_feat['sku'] == sku].sort_values('date').reset_index(drop=True)
        sdf_trainable = sdf.dropna(subset=features + ['demand'])

        if len(sdf_trainable) < 120:
            print(f"Skipping {sku}: too short ({len(sdf_trainable)} rows)")
            continue

        train = sdf_trainable.iloc[:-horizon]
        val = sdf_trainable.iloc[-horizon:]

        X_train = train[features]
        y_train = train['demand']
        X_val = val[features]
        y_val = val['demand']

        model = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.05, verbosity=0)
        model.fit(X_train, y_train)  # plain fit() for compatibility

        # Save model
        joblib.dump(model, os.path.join(models_dir, f'{sku}.joblib'))

        # Validation metrics
        y_val_pred = model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
        mae = mean_absolute_error(y_val, y_val_pred)
        mape = safe_mape(y_val, y_val_pred)
        sm = smape(y_val, y_val_pred)

        # Residual percentiles for prediction intervals
        residuals = y_val.values - y_val_pred
        lower_bound = np.percentile(residuals, lower_q * 100)
        upper_bound = np.percentile(residuals, upper_q * 100)

        # Iterative forecasting
        last_known = sdf.iloc[-max(60, 30):].copy()
        temp = last_known.reset_index(drop=True)
        preds = []

        for day in range(1, horizon + 1):
            next_date = temp['date'].iloc[-1] + pd.Timedelta(days=1)
            new_row = pd.DataFrame([{'date': next_date, 'sku': sku, 'demand': temp['demand'].iloc[-1]}])
            temp = pd.concat([temp, new_row], ignore_index=True)

            # Ensure plant/category columns exist
            if 'plant' not in temp.columns:
                temp['plant'] = 'Plant_1'
            if 'category' not in temp.columns:
                temp['category'] = 'Cat_1'

            temp_feat = create_features(temp[['date', 'sku', 'demand', 'plant', 'category']])
            feat_row = temp_feat.iloc[-1:][features]

            p = model.predict(feat_row)[0]
            lower = max(0, p + lower_bound)
            upper = max(0, p + upper_bound)

            preds.append({
                'sku': sku,
                'date': next_date,
                'forecast': float(round(max(0, p), 3)),
                'lower_q': float(round(lower, 3)),
                'upper_q': float(round(upper, 3))
            })

            temp.at[temp.index[-1], 'demand'] = p

        results.extend(preds)

        metrics.append({
            'sku': sku,
            'rmse': float(round(rmse, 4)),
            'mae': float(round(mae, 4)),
            'mape': float(round(mape, 4)) if not np.isnan(mape) else None,
            'smape': float(round(sm, 4)) if not np.isnan(sm) else None,
            'n_train': len(X_train),
            'n_val': len(X_val)
        })

        print(f"{sku}: RMSE={rmse:.3f}, MAE={mae:.3f}, MAPE={mape if not np.isnan(mape) else 'NA'}%")

    out_df = pd.DataFrame(results)
    metrics_df = pd.DataFrame(metrics)

    if not out_df.empty:
        out_df.to_csv(out_forecast, index=False)
        print(f'Written forecasts -> {out_forecast} ({len(out_df):,} rows)')

    if not metrics_df.empty:
        metrics_df.to_csv(out_metrics, index=False)
        print(f'Written metrics -> {out_metrics} ({len(metrics_df):,} rows)')

    return out_df, metrics_df


if __name__ == '__main__':
    train_and_forecast()
