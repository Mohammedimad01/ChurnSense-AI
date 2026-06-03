# SQL Analytics - ChurnSense-AI


## Prerequisites

Run the notebook pipeline first:

1. `01_data_cleaning.ipynb` → `telco_churn_clean.csv`
2. `02_eda.ipynb` → `churn_by_*.csv`
3. `04_model_training.ipynb` → `model_comparison.csv`
4. `05_model_evaluation.ipynb` → SHAP, threshold, business impact CSVs

## Build analytics database

```powershell
cd "C:\Users\username\Projectfolder"
python sql/build_analytics_db.py
```

Creates `data/processed/churnsense_analytics.db` and auto-generates `customer_scores.csv` if models exist.

Optional manual scoring:

```powershell
python sql/generate_customer_scores.py
python sql/build_analytics_db.py
```

## Query library

| File | Business question | Power BI page |
|------|-------------------|---------------|
| `01_executive_kpis.sql` | Portfolio health snapshot | Executive |
| `02_churn_by_segment.sql` | All segments ranked | Segments |
| `03_contract_tenure_matrix.sql` | Contract × tenure heatmap | Segments |
| `04_model_performance.sql` | Model leaderboard | ML Performance |
| `05_retention_roi.sql` | SHAP, threshold, ROI | Retention ROI |
| `06_high_risk_customers.sql` | ML outreach list | CRM Action |
| `06b_high_risk_rule_based.sql` | EDA rule-based list (no ML) | CRM Action |
| `07_churn_by_contract.sql` | Churn by contract type | Executive / Segments |
| `08_churn_by_payment.sql` | Churn by payment method | Segments |
| `09_high_value_customer_analysis.sql` | Top 25% MRC churn risk | Segments |
| `10_tenure_churn_analysis.sql` | Lifecycle churn curve | Segments |
| `11_monthly_revenue_analysis.sql` | MRR / ARR leakage | Executive |
| `12_customer_segmentation.sql` | CRM campaign segments | CRM Action |

## Run all queries (demo)

```powershell
python sql/run_all_queries.py
```

## SQLite CLI

```powershell
sqlite3 data/processed/churnsense_analytics.db < sql/07_churn_by_contract.sql
```

## Python

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/processed/churnsense_analytics.db")
df = pd.read_sql_query(open("sql/12_customer_segmentation.sql", encoding="utf-8").read(), conn)
print(df.head())
```

## Power BI

See [`../dashboard/POWERBI_GUIDE.md`](../dashboard/POWERBI_GUIDE.md) and [`../dashboard/DAX_MEASURES.txt`](../dashboard/DAX_MEASURES.txt).

**Connect:** Get Data → SQLite → `churnsense_analytics.db`

## PostgreSQL / Azure SQL

- Replace `REAL` with `DOUBLE PRECISION` if needed
- Percentile in `09_*` can use `PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY monthly_charges)`
