"""Example: upload CSV(s) into MySQL tables. Uses SQLAlchemy.
Usage: python export_mysql.py --host localhost --port 3306 --db forecast_db --user root --password pass
"""
"""python export_mysql.py --host MyData_Shine --port 3306 --db forecast_db --user root --password adminsmap

"""



import argparse
import os
import pandas as pd
from sqlalchemy import create_engine


def upload(csv_path, table_name, engine):
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f'Uploaded {len(df):,} rows to {table_name}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', default='3306')
    parser.add_argument('--db', required=True)
    parser.add_argument('--user', required=True)
    parser.add_argument('--password', required=True)
    args = parser.parse_args()
    conn = f"mysql+mysqlconnector://{args.user}:{args.password}@{args.host}:{args.port}/{args.db}"
    engine = create_engine(conn)
    # upload available outputs if present
    for p, t in [('outputs/sku_forecasts_daily.csv','sku_forecasts_daily'), ('outputs/agg_monthly_forecast.csv','agg_monthly_forecast')]:
        try:
            if os.path.exists(p):
                upload(p, t, engine)
            else:
                print('Missing', p)
        except Exception as e:
            print('Failed to upload', p, e)
