"""
Run all ChurnSense-AI SQL analytics files and print row counts.

Usage:
    python sql/build_analytics_db.py
    python sql/generate_customer_scores.py   # optional, for query 06
    python sql/run_all_queries.py
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "churnsense_analytics.db"

QUERY_FILES = [
    "01_executive_kpis.sql",
    "02_churn_by_segment.sql",
    "03_contract_tenure_matrix.sql",
    "04_model_performance.sql",
    "05_retention_roi.sql",
    "06_high_risk_customers.sql",
    "06b_high_risk_rule_based.sql",
    "07_churn_by_contract.sql",
    "08_churn_by_payment.sql",
    "09_high_value_customer_analysis.sql",
    "10_tenure_churn_analysis.sql",
    "11_monthly_revenue_analysis.sql",
    "12_customer_segmentation.sql",
]


def _strip_sql_comments(sql: str) -> str:
    """
    Remove SQL comments while preserving query body.

    Handles:
    - line comments: -- ...
    - block comments: /* ... */
    """
    without_block = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    without_line = re.sub(r"--.*?$", "", without_block, flags=re.MULTILINE)
    return without_line


def _split_sql_statements(sql: str) -> list[str]:
    """Split SQL script into semicolon-delimited statements (non-empty only)."""
    cleaned = _strip_sql_comments(sql)
    return [stmt.strip() for stmt in cleaned.split(";") if stmt.strip()]


def _is_query_statement(stmt: str) -> bool:
    """
    Detect statements that return tabular results for pd.read_sql_query.

    Supports:
    - SELECT ...
    - WITH ... SELECT ...
    """
    normalized = stmt.lstrip()
    if not normalized:
        return False

    upper = normalized.upper()
    if upper.startswith("SELECT"):
        return True

    # CTE queries usually start with WITH and eventually contain a SELECT.
    if upper.startswith("WITH") and re.search(r"\bSELECT\b", upper):
        return True

    return False


def run_sql_file(conn: sqlite3.Connection, path: Path):
    """Execute one file (may contain multiple statements); return last query result."""
    sql = path.read_text(encoding="utf-8")
    statements = _split_sql_statements(sql)

    last_df = None
    import pandas as pd

    for stmt in statements:
        if _is_query_statement(stmt):
            last_df = pd.read_sql_query(stmt, conn)
    return last_df


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"{DB_PATH} not found. Run: python sql/build_analytics_db.py"
        )

    conn = sqlite3.connect(DB_PATH)
    print(f"Database: {DB_PATH}\n")

    import pandas as pd

    for name in QUERY_FILES:
        path = SQL_DIR / name
        if not path.exists():
            print(f"SKIP {name}")
            continue

        sql = path.read_text(encoding="utf-8")
        # Run only query blocks for demo output (SELECT and WITH...SELECT)
        blocks = _split_sql_statements(sql)
        select_blocks = [b for b in blocks if _is_query_statement(b)]

        print(f"=== {name} ({len(select_blocks)} query/queries) ===")
        for i, block in enumerate(select_blocks, 1):
            try:
                df = pd.read_sql_query(block, conn)
                print(f"  Q{i}: {len(df)} rows x {len(df.columns)} cols")
                if len(df) <= 8:
                    print(df.to_string(index=False))
                else:
                    print(df.head(5).to_string(index=False))
                    print("  ...")
            except Exception as exc:
                print(f"  Q{i}: ERROR — {exc}")
        print()

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
