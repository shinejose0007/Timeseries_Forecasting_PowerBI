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

If you want, I can provide M-code snippets for key Power Query transformations and a mock PBIX layout in a follow-up message.
