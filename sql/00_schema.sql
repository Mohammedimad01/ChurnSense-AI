-- ChurnSense-AI — analytics schema (SQLite / PostgreSQL compatible)
-- Run after loading CSVs via: python sql/build_analytics_db.py

-- Core customer table (from telco_churn_clean.csv)
CREATE TABLE IF NOT EXISTS customers (
    customer_id       TEXT PRIMARY KEY,
    gender            TEXT,
    senior_citizen    INTEGER,
    partner           TEXT,
    dependents        TEXT,
    tenure            INTEGER,
    phone_service     TEXT,
    multiple_lines    TEXT,
    internet_service  TEXT,
    online_security   TEXT,
    online_backup     TEXT,
    device_protection TEXT,
    tech_support      TEXT,
    streaming_tv      TEXT,
    streaming_movies  TEXT,
    contract          TEXT,
    paperless_billing TEXT,
    payment_method    TEXT,
    monthly_charges   REAL,
    total_charges     REAL,
    churn             TEXT,
    churn_flag        INTEGER,
    tenure_group      TEXT,
    charge_group      TEXT
);

-- EDA segment summaries (from notebooks/02_eda.ipynb exports)
CREATE TABLE IF NOT EXISTS churn_by_contract (
    contract        TEXT PRIMARY KEY,
    customers       INTEGER,
    churners        INTEGER,
    churn_rate_pct  REAL
);

CREATE TABLE IF NOT EXISTS churn_by_payment (
    payment_method  TEXT PRIMARY KEY,
    customers       INTEGER,
    churners        INTEGER,
    churn_rate_pct  REAL
);

CREATE TABLE IF NOT EXISTS churn_by_tenure_band (
    tenure_group    TEXT PRIMARY KEY,
    customers       INTEGER,
    churners        INTEGER,
    churn_rate_pct  REAL
);

CREATE TABLE IF NOT EXISTS churn_by_charge_band (
    charge_group    TEXT PRIMARY KEY,
    customers       INTEGER,
    churners        INTEGER,
    churn_rate_pct  REAL
);

-- Model leaderboard (from notebooks/04_model_training.ipynb)
CREATE TABLE IF NOT EXISTS model_comparison (
    model           TEXT PRIMARY KEY,
    accuracy        REAL,
    precision_score REAL,
    recall          REAL,
    f1              REAL,
    roc_auc         REAL
);

-- Phase 5 explainability exports
CREATE TABLE IF NOT EXISTS shap_global_importance (
    feature         TEXT PRIMARY KEY,
    mean_abs_shap   REAL
);

CREATE TABLE IF NOT EXISTS threshold_sweep (
    threshold       REAL PRIMARY KEY,
    precision_score REAL,
    recall          REAL,
    f1              REAL,
    flagged_pct     REAL
);

CREATE TABLE IF NOT EXISTS business_impact (
    metric          TEXT PRIMARY KEY,
    value           REAL
);

-- Optional: customer-level scores (populate after inference / Streamlit batch scoring)
CREATE TABLE IF NOT EXISTS customer_scores (
    customer_id       TEXT PRIMARY KEY,
    churn_probability REAL,
    risk_band         TEXT,
    flagged_for_outreach INTEGER,
    scored_at         TEXT
);
