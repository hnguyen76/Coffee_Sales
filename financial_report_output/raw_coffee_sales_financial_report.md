# Financial Report - raw_coffee_sales.csv

Generated at: 2026-05-26 20:07:49

## Executive Summary

- Revenue is $8,360.50 with gross margin of 55.0% and net margin of 55.0%.
- Net profit is $4,595.50 after total expenses of $3,765.00.
- The largest expense bucket is COGS at $3,765.00, which should be reviewed for controllability and trend risk.
- The top region is 'East' with $3,067.00, representing 36.7% of revenue.
- 'Unassigned' has the weakest net margin among top region groups (47.4%); review pricing, cost allocation, and mix.
- The top store is 'Providence Cafe' with $3,257.00, representing 39.0% of revenue.
- 'Providence Cafe' has the weakest net margin among top store groups (51.0%); review pricing, cost allocation, and mix.

## KPI Snapshot

| KPI | Value | Why it matters |
| --- | --- | --- |
| Finance fact rows | 100 | Normalized transaction/line-item rows |
| Revenue | $8,360.50 | Top-line sales or income |
| Gross profit | $4,595.50 | Revenue after COGS |
| Gross margin | 55.0% | Profitability before operating expenses |
| Operating profit | $4,595.50 | Core business profit |
| Net profit | $4,595.50 | Bottom-line profit after all classified lines |
| Net margin | 55.0% | Bottom-line profitability rate |
| Total expenses | $3,765.00 | COGS plus operating/other expenses |
| Periods | 1 | Number of dated reporting periods |

## P&L Summary

| Line Item | Amount | Percent Of Revenue |
| --- | --- | --- |
| Revenue | $8,360.50 | 100.0% |
| COGS | -$3,765.00 | -45.0% |
| Gross Profit | $4,595.50 | 55.0% |
| Operating Profit | $4,595.50 | 55.0% |
| Net Profit | $4,595.50 | 55.0% |

## Monthly Performance

| Period | Revenue | Cogs | Gross Profit | Operating Expense | Operating Profit | Other Income | Other Expense | Tax | Net Profit | Gross Margin | Net Margin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-05 | $8,080.50 | -$3,635.00 | $4,445.50 | $0.00 | $4,445.50 | $0.00 | $0.00 | $0.00 | $4,445.50 | 55.0% | 55.0% |
| Unassigned Period | $280.00 | -$130.00 | $150.00 | $0.00 | $150.00 | $0.00 | $0.00 | $0.00 | $150.00 | 53.6% | 53.6% |

## Driver Analysis

### By Region

| Region | Cogs | Revenue | Gross Profit | Operating Profit | Net Profit | Gross Margin | Net Margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| East | -$1,496.00 | $3,067.00 | $1,571.00 | $1,571.00 | $1,571.00 | 51.2% | 51.2% |
| South | -$1,033.00 | $2,654.00 | $1,621.00 | $1,621.00 | $1,621.00 | 61.1% | 61.1% |
| West | -$1,136.00 | $2,449.50 | $1,313.50 | $1,313.50 | $1,313.50 | 53.6% | 53.6% |
| Unassigned | -$100.00 | $190.00 | $90.00 | $90.00 | $90.00 | 47.4% | 47.4% |

### By Store

| Store | Cogs | Revenue | Gross Profit | Operating Profit | Net Profit | Gross Margin | Net Margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Providence Cafe | -$1,596.00 | $3,257.00 | $1,661.00 | $1,661.00 | $1,661.00 | 51.0% | 51.0% |
| Austin Beans | -$1,033.00 | $2,654.00 | $1,621.00 | $1,621.00 | $1,621.00 | 61.1% | 61.1% |
| Seattle Central | -$1,136.00 | $2,449.50 | $1,313.50 | $1,313.50 | $1,313.50 | 53.6% | 53.6% |

### By Product

| Product | Cogs | Revenue | Gross Profit | Operating Profit | Net Profit | Gross Margin | Net Margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Latte | -$680.00 | $1,255.00 | $575.00 | $575.00 | $575.00 | 45.8% | 45.8% |
| Americano | -$343.00 | $915.00 | $572.00 | $572.00 | $572.00 | 62.5% | 62.5% |
| Espresso | -$359.00 | $880.00 | $521.00 | $521.00 | $521.00 | 59.2% | 59.2% |
| Mocha | -$412.00 | $778.00 | $366.00 | $366.00 | $366.00 | 47.0% | 47.0% |
| Cappuccino | -$334.00 | $619.00 | $285.00 | $285.00 | $285.00 | 46.0% | 46.0% |
| Cold Brew | -$290.00 | $586.00 | $296.00 | $296.00 | $296.00 | 50.5% | 50.5% |
| Chai Latte | -$231.00 | $524.00 | $293.00 | $293.00 | $293.00 | 55.9% | 55.9% |
| Bagel | -$212.00 | $520.00 | $308.00 | $308.00 | $308.00 | 59.2% | 59.2% |
| Cookie | -$135.00 | $435.00 | $300.00 | $300.00 | $300.00 | 69.0% | 69.0% |
| Green Tea | -$130.00 | $372.50 | $242.50 | $242.50 | $242.50 | 65.1% | 65.1% |


## Data Quality And Controls

| Check | Result |
| --- | --- |
| Original shape | 52 rows x 10 columns |
| Cleaned shape | 50 rows x 10 columns |
| Finance fact rows | 100 |
| Amount source | revenue/cost columns |
| Duplicate rows removed | 2 |
| Date columns parsed | date (96%) |
| Numeric columns converted | units_sold (96%), revenue (100%), cost (100%) |
| Missing values handled | date: kept as missing date; region: filled 1 with Unassigned; units_sold: filled 2 with median 35.0; discount_percent: filled 2 with 0 |
| Unclassified finance rows | 0 |

## Recommendations

- Validate the financial sign convention with Finance: this template reports income as positive and costs/expenses as negative.
- Lock a data dictionary for account, account type, scenario, and cost center fields to reduce manual mapping risk.
- Use gross margin by product, store, department, or region to find where profitable growth can scale.
- Build a recurring driver view by region to separate revenue growth from margin dilution.
- Add Budget or Forecast data to enable variance analysis and a more complete finance review cadence.

## Output Files

- Cleaned CSV: `C:/Users/hieum/Desktop/Repo/Coffee_sales/Coffee_Sales/financial_report_output/raw_coffee_sales_cleaned.csv`
- Finance fact CSV: `C:/Users/hieum/Desktop/Repo/Coffee_sales/Coffee_Sales/financial_report_output/raw_coffee_sales_finance_fact.csv`
- Excel workbook: `C:/Users/hieum/Desktop/Repo/Coffee_sales/Coffee_Sales/financial_report_output/raw_coffee_sales_financial_workbook.xlsx`
- Charts:
  - `C:/Users/hieum/Desktop/Repo/Coffee_sales/Coffee_Sales/financial_report_output/charts/monthly_pnl_trend.png`
  - `C:/Users/hieum/Desktop/Repo/Coffee_sales/Coffee_Sales/financial_report_output/charts/pnl_summary.png`
  - `C:/Users/hieum/Desktop/Repo/Coffee_sales/Coffee_Sales/financial_report_output/charts/top_expense_drivers.png`
  - `C:/Users/hieum/Desktop/Repo/Coffee_sales/Coffee_Sales/financial_report_output/charts/margin_trend.png`
  - `C:/Users/hieum/Desktop/Repo/Coffee_sales/Coffee_Sales/financial_report_output/charts/profitability_by_region.png`

## Assumptions

- P&L sign convention is income positive and costs/expenses negative unless `--sign-mode as-is` is used.
- If the CSV has separate revenue and cost columns, the template creates two finance fact rows per source row.
- If Actual/Budget/Forecast/Prior columns exist, they are melted into scenario rows for variance analysis.
- Auto-inference is a starting point; use CLI column overrides for production reporting.
