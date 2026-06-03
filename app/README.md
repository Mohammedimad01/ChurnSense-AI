# ChurnSense-AI Streamlit App

Live churn scoring and retention recommendations for telecom CRM teams.

## Prerequisites

Run notebooks **01, 03, 04, 05** so these files exist:

models/preprocessor.joblib
models/best_model.joblib
models/churn_threshold.json
data/processed/X_train.csv   # SHAP background sample

## Run locally

powershell
cd "C:\Users\username\folder"
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/app.py

Opens at `http://localhostport`

## Features

| Page | Description |
|------|-------------|
| **Dashboard** | Portfolio KPIs + risk distribution (after batch export) |
| **Single customer** | Form scoring, SHAP drivers, retention tips |
| **Batch scoring** | CSV upload → outreach list → export for SQL/Power BI |
| **About** | Model metadata and pipeline checklist |

## After batch scoring

Re-build analytics DB so Power BI Page 5 has scores:

powershell
python sql/build_analytics_db.py

## Demo presets (sidebar)

- **High-risk MTM** - month-to-month, low tenure, electronic check
- **Loyal long-term** - two-year contract, high tenure
