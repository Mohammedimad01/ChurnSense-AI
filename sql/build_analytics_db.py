"""
Build ChurnSense-AI SQLite analytics database from processed CSV exports.

Usage:
    python sql/build_analytics_db.py

Prerequisites:
    Run notebooks 01–05 so data/processed/ contains the expected CSV files.
    At minimum, telco_churn_clean.csv is required; other tables load if present.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SQL_DIR = Path(__file__).resolve().parent
DB_PATH = PROCESSED_DIR / "churnsense_analytics.db"

TENURE_BINS = [0, 6, 12, 24, 48, 72, 1000]
TENURE_LABELS = ["0-6 mo", "7-12 mo", "13-24 mo", "25-48 mo", "49-72 mo", "73+ mo"]
CHARGE_BINS = [0, 35, 55, 75, 95, 200]
CHARGE_LABELS = ["$0-35", "$35-55", "$55-75", "$75-95", "$95+"]


def _load_customers(conn: sqlite3.Connection) -> None:
    clean_path = PROCESSED_DIR / "telco_churn_clean.csv"
    if not clean_path.exists():
        raise FileNotFoundError(
            f"Missing {clean_path}. Run notebooks/01_data_cleaning.ipynb first."
        )

    df = pd.read_csv(clean_path)
    df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)
    df["TenureGroup"] = pd.cut(
        df["tenure"], bins=TENURE_BINS, labels=TENURE_LABELS, right=True
    )
    df["ChargeGroup"] = pd.cut(
        df["MonthlyCharges"], bins=CHARGE_BINS, labels=CHARGE_LABELS
    )

    out = pd.DataFrame(
        {
            "customer_id": df["customerID"],
            "gender": df["gender"],
            "senior_citizen": df["SeniorCitizen"],
            "partner": df["Partner"],
            "dependents": df["Dependents"],
            "tenure": df["tenure"],
            "phone_service": df["PhoneService"],
            "multiple_lines": df["MultipleLines"],
            "internet_service": df["InternetService"],
            "online_security": df["OnlineSecurity"],
            "online_backup": df["OnlineBackup"],
            "device_protection": df["DeviceProtection"],
            "tech_support": df["TechSupport"],
            "streaming_tv": df["StreamingTV"],
            "streaming_movies": df["StreamingMovies"],
            "contract": df["Contract"],
            "paperless_billing": df["PaperlessBilling"],
            "payment_method": df["PaymentMethod"],
            "monthly_charges": df["MonthlyCharges"],
            "total_charges": df["TotalCharges"],
            "churn": df["Churn"],
            "churn_flag": df["ChurnFlag"],
            "tenure_group": df["TenureGroup"].astype(str),
            "charge_group": df["ChargeGroup"].astype(str),
        }
    )
    out.to_sql("customers", conn, if_exists="replace", index=False)


def _load_csv_table(
    conn: sqlite3.Connection,
    csv_name: str,
    table_name: str,
    rename: dict[str, str] | None = None,
) -> bool:
    path = PROCESSED_DIR / csv_name
    if not path.exists():
        print(f"  skip {table_name} ({csv_name} not found)")
        return False

    df = pd.read_csv(path, index_col=0 if csv_name.startswith("churn_by_") else None)
    df = df.reset_index()
    if rename:
        df = df.rename(columns=rename)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"  loaded {table_name} ({len(df)} rows)")
    return True


def _ensure_customer_scores() -> None:
    """Create customer_scores.csv when models exist but scores were not exported yet."""
    scores_path = PROCESSED_DIR / "customer_scores.csv"
    if scores_path.exists():
        return
    if not (PROJECT_ROOT / "models" / "best_model.joblib").exists():
        print("  skip customer_scores (train models in notebook 04 first)")
        return

    print("Generating customer_scores.csv via batch inference...")
    import sys

    sys.path.insert(0, str(PROJECT_ROOT))
    from src.features import load_clean_data
    from src.inference import export_customer_scores, load_inference_bundle, score_customers

    df = load_clean_data(
        PROCESSED_DIR / "telco_churn_clean.csv",
        PROJECT_ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv",
    )
    bundle = load_inference_bundle(PROJECT_ROOT / "models", PROCESSED_DIR)
    scores = score_customers(df, bundle["model"], bundle["preprocessor"], bundle["threshold"])
    export_customer_scores(scores, scores_path)
    print(f"  wrote customer_scores ({len(scores):,} rows)")


def build_database(db_path: Path = DB_PATH) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    _ensure_customer_scores()

    conn = sqlite3.connect(db_path)
    try:
        schema = (SQL_DIR / "00_schema.sql").read_text(encoding="utf-8")
        conn.executescript(schema)

        print("Loading customers...")
        _load_customers(conn)

        print("Loading segment / model exports...")
        _load_csv_table(conn, "churn_by_contract.csv", "churn_by_contract", {"Contract": "contract"})
        _load_csv_table(conn, "churn_by_payment.csv", "churn_by_payment", {"PaymentMethod": "payment_method"})
        _load_csv_table(conn, "churn_by_tenure_band.csv", "churn_by_tenure_band", {"TenureGroup": "tenure_group"})
        _load_csv_table(conn, "churn_by_charge_band.csv", "churn_by_charge_band", {"ChargeGroup": "charge_group"})
        _load_csv_table(
            conn,
            "model_comparison.csv",
            "model_comparison",
            {"precision": "precision_score"},
        )
        _load_csv_table(conn, "shap_global_importance.csv", "shap_global_importance")
        _load_csv_table(
            conn,
            "threshold_sweep.csv",
            "threshold_sweep",
            {"precision": "precision_score"},
        )
        _load_csv_table(conn, "business_impact_summary.csv", "business_impact", {"metric": "metric", "value": "value"})

        scores_path = PROCESSED_DIR / "customer_scores.csv"
        if scores_path.exists():
            scores = pd.read_csv(scores_path)
            scores.to_sql("customer_scores", conn, if_exists="replace", index=False)
            print(f"  loaded customer_scores ({len(scores)} rows)")
        else:
            print("  skip customer_scores (run Streamlit batch scoring first)")

        conn.commit()
    finally:
        conn.close()

    print(f"\nAnalytics DB ready: {db_path}")
    return db_path


if __name__ == "__main__":
    build_database()
