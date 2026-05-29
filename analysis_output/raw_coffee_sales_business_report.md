# Business Insight Report - raw_coffee_sales.csv

Generated at: 2026-05-28 21:47:21

## Executive Summary

- Total revenue is $8,360.50 across 50 cleaned rows.
- Overall gross margin is 55.0%; this KPI should be tracked alongside revenue growth.
- Revenue in the final period increased by 16.7% versus the first period ($638.50 -> $745.00).
- The strongest region is 'East' with $3,067.00, contributing 36.7% of revenue.
- Within region groups, 'Unknown' has the lowest margin (47.4%) among top revenue groups; review pricing, COGS, or promotion strategy.
- The strongest store is 'Providence Cafe' with $3,257.00, contributing 39.0% of revenue.
- Within store groups, 'Providence Cafe' has the lowest margin (51.0%) among top revenue groups; review pricing, COGS, or promotion strategy.
- The strongest category is 'Coffee' with $5,365.00, contributing 64.2% of revenue.
- Within category groups, 'Coffee' has the lowest margin (51.8%) among top revenue groups; review pricing, COGS, or promotion strategy.
- Discounted rows have an average margin of 55.6%, 1.2 percentage points lower than non-discounted rows. This is a signal to evaluate whether promotions are creating value or eroding profit.

## KPI Snapshot

| KPI | Value | Why it matters |
| --- | --- | --- |
| Rows after cleaning | 50 | Dataset size used for analysis |
| Period | 2026-05-01 -> 2026-05-13 | Available data period |
| Total revenue | $8,360.50 | Total sales/revenue |
| Gross profit | $4,595.50 | Gross profit after cost |
| Blended margin | 55.0% | Overall gross profit margin |
| Units sold | 2,014 | Total volume sold |
| Transactions | 50 | Unique orders/transactions |
| Avg discount | 3.6% | Average discount rate |

## Data Quality Summary

| Check | Result |
| --- | --- |
| Original shape | 52 rows x 10 columns |
| Shape after cleaning/metrics | 50 rows x 17 columns |
| Duplicate rows removed | 2 |
| Date columns parsed | date (96%) |
| Numeric columns converted | units_sold (96%), revenue (100%), cost (100%) |
| Missing values handled | date: kept as missing date; region: filled 1 with Unknown; units_sold: filled 2 with 35.0; discount_percent: filled 2 with 0 |

## Dimension Performance

### Top Region

| Region | Revenue | Profit | Margin | Units |
| --- | --- | --- | --- | --- |
| East | $3,067.00 | $1,571.00 | 51.2% | 640 |
| South | $2,654.00 | $1,621.00 | 61.1% | 806 |
| West | $2,449.50 | $1,313.50 | 53.6% | 533 |
| Unknown | $190.00 | $90.00 | 47.4% | 35 |

### Top Store

| Store | Revenue | Profit | Margin | Units |
| --- | --- | --- | --- | --- |
| Providence Cafe | $3,257.00 | $1,661.00 | 51.0% | 675 |
| Austin Beans | $2,654.00 | $1,621.00 | 61.1% | 806 |
| Seattle Central | $2,449.50 | $1,313.50 | 53.6% | 533 |

### Top Category

| Category | Revenue | Profit | Margin | Units |
| --- | --- | --- | --- | --- |
| Coffee | $5,365.00 | $2,781.00 | 51.8% | 1,196 |
| Food | $1,739.00 | $1,072.00 | 61.6% | 517 |
| Tea | $1,256.50 | $742.50 | 59.1% | 301 |

## Recommendations

- Double down on 'East' in the region dimension: review inventory, staffing, campaigns, and cross-sell opportunities to expand the revenue-driving group.
- Investigate the margin for 'East' (region): revenue is meaningful, but margin is only 51.2%. Prioritize reviewing cost, price packs, discounting, and product mix.
- Split promotions into clear cohorts: no discount, light discount, and deep discount. Compare incremental revenue with margin loss before increasing promotional spend.
- Build a daily/weekly dashboard for revenue, gross profit, and margin to detect slow sales days, stockout risk, or underperforming campaigns early.

## Output Files

- Cleaned CSV: `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/raw_coffee_sales_cleaned.csv`
- Charts:
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/revenue_profit_trend.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/top_region_by_revenue.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/margin_by_region.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/top_store_by_revenue.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/margin_by_store.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/top_category_by_revenue.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/margin_by_category.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/top_product_by_revenue.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/margin_by_product.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/discount_vs_profit_margin.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/numeric_correlation_heatmap.png`
  - `C:/Users/hueyn/Desktop/Coffee_Sales/analysis_output/charts/missing_values_before_cleaning.png`

## Suggested Next Analyst Steps

- Validate business definitions: revenue gross/net, cost/COGS, discount before/after tax.
- Add a data dictionary for each column to reduce the risk of incorrect auto-inference.
- Add targets/forecasts to turn this report into variance analysis.
- Connect the cleaned CSV output to a BI dashboard if this pipeline runs daily.
