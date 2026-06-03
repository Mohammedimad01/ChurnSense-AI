"""
Batch-score all customers and export customer_scores.csv for SQL / Power BI.

Usage:
    python sql/generate_customer_scores.py
    python sql/build_analytics_db.py   # reloads scores into SQLite
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.features import load_clean_data
from src.inference import export_customer_scores, load_inference_bundle, score_customers

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
CLEAN_PATH = PROCESSED_DIR / "telco_churn_clean.csv"
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
SCORES_PATH = PROCESSED_DIR / "customer_scores.csv"


def main() -> None:
    print("Loading customers...")
    df = load_clean_data(CLEAN_PATH, RAW_PATH)

    print("Loading model bundle...")
    bundle = load_inference_bundle(MODELS_DIR, PROCESSED_DIR)

    print(f"Scoring {len(df):,} customers (threshold={bundle['threshold']:.3f})...")
    scores = score_customers(df, bundle["model"], bundle["preprocessor"], bundle["threshold"])

    path = export_customer_scores(scores, SCORES_PATH)
    flagged = int(scores["flagged_for_outreach"].sum())
    print(f"Saved {path}")
    print(f"Flagged for outreach: {flagged:,} ({100 * flagged / len(scores):.1f}%)")


if __name__ == "__main__":
    main()
