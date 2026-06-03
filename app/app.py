"""
ChurnSense-AI — Streamlit retention scoring app.

Run from project root:
    streamlit run app/app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.inference import (  # noqa: E402
    DEFAULT_CUSTOMER,
    FIELD_OPTIONS,
    customer_dict_to_frame,
    explain_customer,
    export_customer_scores,
    load_inference_bundle,
    retention_recommendations,
    score_customers,
    transform_features,
)

MODELS_DIR = PROJECT_ROOT / "models"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SCORES_EXPORT = PROCESSED_DIR / "customer_scores.csv"
CLEAN_DATA = PROCESSED_DIR / "telco_churn_clean.csv"

# Demo profiles for sidebar quick-load
DEMO_PRESETS: dict[str, dict] = {
    "Custom (default)": DEFAULT_CUSTOMER,
    "High-risk MTM": {
        **DEFAULT_CUSTOMER,
        "customerID": "RISK-00001",
        "Contract": "Month-to-month",
        "tenure": 4,
        "PaymentMethod": "Electronic check",
        "InternetService": "Fiber optic",
        "TechSupport": "No",
        "OnlineSecurity": "No",
        "MonthlyCharges": 95.0,
        "TotalCharges": 380.0,
    },
    "Loyal long-term": {
        **DEFAULT_CUSTOMER,
        "customerID": "LOYAL-00001",
        "Contract": "Two year",
        "tenure": 48,
        "PaymentMethod": "Bank transfer (automatic)",
        "InternetService": "DSL",
        "TechSupport": "Yes",
        "OnlineSecurity": "Yes",
        "MonthlyCharges": 55.0,
        "TotalCharges": 2640.0,
    },
    "Early-life fiber": {
        **DEFAULT_CUSTOMER,
        "customerID": "NEW-00001",
        "Contract": "Month-to-month",
        "tenure": 2,
        "InternetService": "Fiber optic",
        "MonthlyCharges": 85.0,
        "TotalCharges": 170.0,
    },
}


def _option_index(options: list, value, default: int = 0) -> int:
    try:
        return options.index(value)
    except ValueError:
        return default


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        .main-header {
            background: linear-gradient(90deg, #1a5276 0%, #2980b9 100%);
            padding: 1.2rem 1.5rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 1rem;
        }
        .main-header h1 { color: white !important; margin: 0; font-size: 1.8rem; }
        .main-header p { color: #ecf0f1; margin: 0.3rem 0 0 0; }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e0e6ed;
            border-radius: 8px;
            padding: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="main-header">
            <h1>ChurnSense-AI</h1>
            <p>Telecom customer retention intelligence — predict, explain, act</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _risk_color(band: str) -> str:
    return {
        "Low": "#27ae60",
        "Medium": "#f39c12",
        "High": "#e67e22",
        "Critical": "#e74c3c",
    }.get(band, "#1a5276")


@st.cache_resource(show_spinner="Loading model and preprocessor…")
def get_bundle():
    return load_inference_bundle(MODELS_DIR, PROCESSED_DIR)


@st.cache_data(show_spinner=False)
def load_portfolio_scores() -> pd.DataFrame | None:
    if SCORES_EXPORT.exists():
        return pd.read_csv(SCORES_EXPORT)
    return None


@st.cache_data(show_spinner=False)
def load_model_leaderboard() -> pd.DataFrame | None:
    path = PROCESSED_DIR / "model_comparison.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


def render_score_gauge(probability: float, threshold: float, risk_band: str) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Churn probability", f"{probability:.1%}")
    c2.metric("Risk band", risk_band)
    c3.metric("CRM threshold", f"{threshold:.2f}")

    st.progress(min(max(probability, 0.0), 1.0))
    flagged = probability >= threshold
    st.markdown(
        f"**Flagged for outreach:** "
        f"<span style='color:{'#e74c3c' if flagged else '#27ae60'};font-weight:700'>"
        f"{'YES — assign to retention team' if flagged else 'No — monitor only'}</span>",
        unsafe_allow_html=True,
    )


def page_dashboard(bundle: dict) -> None:
    st.subheader("Retention dashboard")
    st.caption("Portfolio view — run batch scoring or `python sql/generate_customer_scores.py` to refresh.")

    scores = load_portfolio_scores()

    if scores is None and CLEAN_DATA.exists():
        st.warning("No `customer_scores.csv` yet. Use **Batch scoring** or run `python sql/generate_customer_scores.py`.")
        if st.button("Score full portfolio now (7k customers)", type="primary"):
            with st.spinner("Scoring portfolio…"):
                df = pd.read_csv(CLEAN_DATA)
                scored = score_customers(
                    df, bundle["model"], bundle["preprocessor"], bundle["threshold"]
                )
                export_customer_scores(scored, SCORES_EXPORT)
                st.cache_data.clear()
                st.success("Portfolio scored. Refreshing dashboard…")
                st.rerun()
        return

    if scores is None:
        st.info("Train models (notebooks 04–05) then score customers to populate this dashboard.")
        return

    flagged = scores[scores["flagged_for_outreach"] == 1]
    critical = scores[scores["risk_band"] == "Critical"]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Customers scored", f"{len(scores):,}")
    m2.metric("Flagged for outreach", f"{len(flagged):,}")
    m3.metric("Critical risk", f"{len(critical):,}")
    m4.metric("Avg churn probability", f"{scores['churn_probability'].mean():.1%}")
    m5.metric("Scoring threshold", f"{bundle['threshold']:.2f}")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Risk band distribution")
        band_order = ["Low", "Medium", "High", "Critical"]
        band_counts = scores["risk_band"].value_counts().reindex(band_order).fillna(0)
        st.bar_chart(band_counts)

    with col_b:
        st.markdown("#### Top 10 highest risk")
        display_cols = [c for c in ["customer_id", "churn_probability", "risk_band"] if c in scores.columns]
        st.dataframe(
            scores.nlargest(10, "churn_probability")[display_cols],
            use_container_width=True,
            hide_index=True,
        )

    leaderboard = load_model_leaderboard()
    if leaderboard is not None:
        st.markdown("#### Model leaderboard (test set)")
        st.dataframe(
            leaderboard.sort_values("roc_auc", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


def page_single_customer(bundle: dict, preset: dict) -> None:
    st.subheader("Score a single customer")
    st.caption("Predict churn risk, explain drivers (SHAP), and get retention recommendations.")

    base = preset.copy()

    with st.form("customer_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            customer_id = st.text_input("Customer ID", value=base["customerID"])
            gender = st.selectbox("Gender", FIELD_OPTIONS["gender"], index=_option_index(FIELD_OPTIONS["gender"], base["gender"]))
            senior = st.selectbox(
                "Senior citizen",
                FIELD_OPTIONS["SeniorCitizen"],
                index=_option_index(FIELD_OPTIONS["SeniorCitizen"], base["SeniorCitizen"]),
                format_func=lambda x: "Yes" if x == 1 else "No",
            )
            partner = st.selectbox("Partner", FIELD_OPTIONS["Partner"], index=_option_index(FIELD_OPTIONS["Partner"], base["Partner"]))
            dependents = st.selectbox("Dependents", FIELD_OPTIONS["Dependents"], index=_option_index(FIELD_OPTIONS["Dependents"], base["Dependents"]))
            tenure = st.number_input("Tenure (months)", min_value=0, max_value=100, value=int(base["tenure"]))

        with col2:
            phone = st.selectbox("Phone service", FIELD_OPTIONS["PhoneService"], index=_option_index(FIELD_OPTIONS["PhoneService"], base["PhoneService"]))
            multiple_lines = st.selectbox("Multiple lines", FIELD_OPTIONS["MultipleLines"], index=_option_index(FIELD_OPTIONS["MultipleLines"], base["MultipleLines"]))
            internet = st.selectbox("Internet service", FIELD_OPTIONS["InternetService"], index=_option_index(FIELD_OPTIONS["InternetService"], base["InternetService"]))
            online_security = st.selectbox("Online security", FIELD_OPTIONS["OnlineSecurity"], index=_option_index(FIELD_OPTIONS["OnlineSecurity"], base["OnlineSecurity"]))
            online_backup = st.selectbox("Online backup", FIELD_OPTIONS["OnlineBackup"], index=_option_index(FIELD_OPTIONS["OnlineBackup"], base["OnlineBackup"]))
            device_protection = st.selectbox("Device protection", FIELD_OPTIONS["DeviceProtection"], index=_option_index(FIELD_OPTIONS["DeviceProtection"], base["DeviceProtection"]))

        with col3:
            tech_support = st.selectbox("Tech support", FIELD_OPTIONS["TechSupport"], index=_option_index(FIELD_OPTIONS["TechSupport"], base["TechSupport"]))
            streaming_tv = st.selectbox("Streaming TV", FIELD_OPTIONS["StreamingTV"], index=_option_index(FIELD_OPTIONS["StreamingTV"], base["StreamingTV"]))
            streaming_movies = st.selectbox("Streaming movies", FIELD_OPTIONS["StreamingMovies"], index=_option_index(FIELD_OPTIONS["StreamingMovies"], base["StreamingMovies"]))
            contract = st.selectbox("Contract", FIELD_OPTIONS["Contract"], index=_option_index(FIELD_OPTIONS["Contract"], base["Contract"]))
            paperless = st.selectbox("Paperless billing", FIELD_OPTIONS["PaperlessBilling"], index=_option_index(FIELD_OPTIONS["PaperlessBilling"], base["PaperlessBilling"]))
            payment = st.selectbox("Payment method", FIELD_OPTIONS["PaymentMethod"], index=_option_index(FIELD_OPTIONS["PaymentMethod"], base["PaymentMethod"]))
            monthly_charges = st.number_input("Monthly charges ($)", min_value=0.0, value=float(base["MonthlyCharges"]))
            total_charges = st.number_input("Total charges ($)", min_value=0.0, value=float(base["TotalCharges"]))

        submitted = st.form_submit_button("Predict churn risk", type="primary", use_container_width=True)

    if not submitted:
        return

    customer = {
        "customerID": customer_id,
        "gender": gender,
        "SeniorCitizen": senior,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone,
        "MultipleLines": multiple_lines,
        "InternetService": internet,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
    }

    df = customer_dict_to_frame(customer)
    scored = score_customers(df, bundle["model"], bundle["preprocessor"], bundle["threshold"])
    row = scored.iloc[0]
    probability = float(row["churn_probability"])
    risk_band = str(row["risk_band"])

    st.divider()
    render_score_gauge(probability, bundle["threshold"], risk_band)

    shap_df = None
    if bundle["X_train"] is not None:
        with st.spinner("Computing SHAP explanation…"):
            try:
                X_enc = transform_features(df, bundle["preprocessor"])
                shap_df = explain_customer(
                    bundle["model"],
                    X_enc,
                    bundle["feature_names"],
                    bundle["X_train"],
                    row_index=0,
                )
            except Exception as exc:  # noqa: BLE001
                st.warning(f"SHAP unavailable: {exc}")

    left, right = st.columns(2)

    with left:
        st.markdown("#### Retention recommendations")
        for tip in retention_recommendations(customer, shap_df):
            st.markdown(f"- {tip}")

    with right:
        if shap_df is not None:
            st.markdown("#### Top model drivers (SHAP)")
            st.bar_chart(shap_df.set_index("feature")["shap_value"])
            st.dataframe(shap_df, use_container_width=True, hide_index=True)


def page_batch_scoring(bundle: dict) -> None:
    st.subheader("Batch scoring")
    st.caption("Upload Telco-format CSV → export outreach list for CRM / Power BI / SQL.")

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader("Customer CSV", type=["csv"])
    with col2:
        use_clean = st.checkbox("Use bundled clean data", value=False, help=str(CLEAN_DATA.name))

    raw_df: pd.DataFrame | None = None

    if use_clean and CLEAN_DATA.exists():
        raw_df = pd.read_csv(CLEAN_DATA)
        st.success(f"Loaded clean portfolio: **{len(raw_df):,}** customers")
    elif uploaded is not None:
        raw_df = pd.read_csv(uploaded)
        st.write(f"Loaded **{len(raw_df):,}** rows from upload")

    if raw_df is None:
        st.info("Upload a CSV or enable bundled clean data (`data/processed/telco_churn_clean.csv`).")
        return

    if st.button("Score all customers", type="primary"):
        with st.spinner("Scoring…"):
            scores = score_customers(raw_df, bundle["model"], bundle["preprocessor"], bundle["threshold"])

        # Optional validation if ground-truth churn column exists
        if "Churn" in raw_df.columns:
            actual = (raw_df["Churn"] == "Yes").astype(int).values
            pred = scores["predicted_churn"].values
            accuracy = (actual == pred).mean()
            st.caption(f"Holdout-style check on uploaded labels — accuracy @ threshold: **{accuracy:.1%}**")

        flagged = scores[scores["flagged_for_outreach"] == 1].sort_values("churn_probability", ascending=False)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Customers scored", f"{len(scores):,}")
        m2.metric("Flagged for outreach", f"{len(flagged):,}")
        m3.metric("Avg churn probability", f"{scores['churn_probability'].mean():.1%}")
        m4.metric("Critical risk", f"{(scores['risk_band'] == 'Critical').sum():,}")

        st.markdown("#### Risk band distribution")
        band_counts = scores["risk_band"].value_counts().reindex(["Low", "Medium", "High", "Critical"]).fillna(0)
        st.bar_chart(band_counts)

        st.markdown("#### High-priority outreach list (top 100)")
        st.dataframe(flagged.head(100), use_container_width=True, hide_index=True)

        export_path = export_customer_scores(scores, SCORES_EXPORT)
        st.cache_data.clear()
        st.success(f"Saved `{export_path.relative_to(PROJECT_ROOT)}` — re-run `python sql/build_analytics_db.py` for Power BI.")

        st.download_button(
            "Download scores CSV",
            scores.to_csv(index=False).encode("utf-8"),
            file_name="customer_scores.csv",
            mime="text/csv",
            use_container_width=True,
        )


def page_about(bundle: dict) -> None:
    st.subheader("About ChurnSense-AI")

    st.markdown(
        """
        End-to-end **telecom churn intelligence** portfolio project:

        | Phase | Deliverable |
        |-------|-------------|
        | 1–2 | Data cleaning & EDA |
        | 3 | Feature engineering + SMOTE |
        | 4 | LR, DT, RF, XGBoost comparison |
        | 5 | SHAP + threshold tuning + ROI |
        | 6 | SQL analytics + Power BI guide |
        | 7 | **This app** — live scoring |
        """
    )

    st.markdown("#### Loaded production bundle")
    meta = {
        "model": bundle["model_name"],
        "scoring_threshold": bundle["threshold"],
        "encoded_features": len(bundle["feature_names"]),
    }
    summary_path = MODELS_DIR / "training_summary.json"
    if summary_path.exists():
        meta["training_summary"] = json.loads(summary_path.read_text(encoding="utf-8"))
    st.json(meta)

    st.markdown("#### Architecture")
    st.code(
        """
Raw CSV → Clean → Encode/Scale → Train models → SHAP + threshold
                ↓                              ↓
         SQL / Power BI              Streamlit scoring (you are here)
        """,
        language="text",
    )

    st.markdown("#### Reference paper family")
    st.markdown(
        "- Chang et al. (2024) *Algorithms* — [10.3390/a17060231](https://doi.org/10.3390/a17060231)"
    )


def main() -> None:
    st.set_page_config(
        page_title="ChurnSense-AI",
        page_icon="📡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_custom_css()
    render_header()

    try:
        bundle = get_bundle()
    except FileNotFoundError as exc:
        st.error("Model artifacts missing. Complete notebooks 01 → 05 first.")
        st.code(str(exc))
        st.markdown(
            """
            **Required files:**
            - `models/preprocessor.joblib`
            - `models/best_model.joblib`
            - `models/churn_threshold.json` (optional, defaults to 0.5)
            """
        )
        st.stop()

    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "Go to",
            ["Dashboard", "Single customer", "Batch scoring", "About"],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("**Production model**")
        st.markdown(f"- {bundle['model_name']}")
        st.markdown(f"- Threshold: `{bundle['threshold']:.2f}`")

        if page == "Single customer":
            st.divider()
            st.markdown("**Demo preset**")
            preset_name = st.selectbox("Load profile", list(DEMO_PRESETS.keys()), label_visibility="collapsed")
        else:
            preset_name = "Custom (default)"

    preset = DEMO_PRESETS.get(preset_name, DEFAULT_CUSTOMER)

    if page == "Dashboard":
        page_dashboard(bundle)
    elif page == "Single customer":
        page_single_customer(bundle, preset)
    elif page == "Batch scoring":
        page_batch_scoring(bundle)
    else:
        page_about(bundle)

    st.sidebar.divider()
    st.sidebar.caption("ChurnSense-AI · Portfolio ML + Analytics")


if __name__ == "__main__":
    main()
