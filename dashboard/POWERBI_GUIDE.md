# Power BI Dashboard Guide — ChurnSense-AI (Phase 6)

Build a **5-page retention intelligence dashboard** connected to `data/processed/churnsense_analytics.db` (or CSV imports from `data/processed/`).

---

## Data model

### Tables to import

| Table | Source | Role |
|-------|--------|------|
| `customers` | `telco_churn_clean.csv` or SQLite | Fact — 7,043 customers |
| `churn_by_contract` | EDA export | Segment summary |
| `churn_by_payment` | EDA export | Segment summary |
| `churn_by_tenure_band` | EDA export | Segment summary |
| `churn_by_charge_band` | EDA export | Segment summary |
| `model_comparison` | Phase 4 | ML leaderboard |
| `shap_global_importance` | Phase 5 | Feature drivers |
| `threshold_sweep` | Phase 5 | Threshold tuning |
| `business_impact` | Phase 5 | ROI metrics |

### Relationships

- No FK required for summary tables (standalone visuals).
- Optional: `customer_scores[customer_id]` → `customers[customer_id]` when Phase 7 scoring is added.

---

## Theme & branding

| Element | Value |
|---------|-------|
| Primary | `#1a5276` (telecom blue) |
| Accent / alert | `#e74c3c` (churn red) |
| Success | `#27ae60` |
| Font | Segoe UI |
| Title | **ChurnSense-AI — Retention Intelligence** |

---

## Page 1 — Executive Overview

**Audience:** VP Retention, monthly business review

| Visual | Type | Data / measure |
|--------|------|----------------|
| Total customers | Card | `COUNT(customers[customer_id])` |
| Overall churn rate | Card | `% Churn Rate` (DAX) |
| Revenue at risk (annual) | Card | `[Annual Revenue at Risk]` |
| Total MRR / ARR | Card | `11_monthly_revenue_analysis.sql` (summary) |
| Churn by contract | Clustered bar | `07_churn_by_contract.sql` |
| Customer mix | Donut | `customers[contract]` |
| MTM share | KPI | `[MTM Customer %]` |

**Slicers:** Contract, Payment Method, Tenure Group (on `customers`)

```
┌─────────────────────────────────────────────────────────────┐
│  ChurnSense-AI — Retention Intelligence    [Contract ▼]     │
├──────────┬──────────┬──────────┬──────────────────────────────┤
│ Customers│ Churn %  │ ARR Risk │  Churn by Contract (bar)    │
│  7,043   │  26.5%   │  $1.2M   │                              │
├──────────┴──────────┴──────────┴──────────────────────────────┤
│  Revenue by Charge Band (11_monthly_revenue) │ Contract Donut │
└─────────────────────────────────────────────────────────────┘
```

---

## Page 2 — Segment Deep Dive

| Visual | Type | Data / SQL |
|--------|------|------------|
| Churn by segment | Bar chart (horizontal) | `02_churn_by_segment.sql` |
| Contract × Tenure matrix | Matrix + conditional formatting | `03_contract_tenure_matrix.sql` |
| Churn by contract | Bar | `07_churn_by_contract.sql` |
| Churn by payment | Bar | `08_churn_by_payment.sql` |
| High-value churn | Clustered bar | `09_high_value_customer_analysis.sql` |
| Tenure lifecycle | Line chart | `10_tenure_churn_analysis.sql` |
| CRM segments | Donut | `12_customer_segmentation.sql` (summary query) |

**Insight callout (text box):**
> Month-to-month + tenure &lt; 12 months = highest-risk cohort. Prioritize contract migration offers.

---

## Page 3 — Model Performance

| Visual | Type | Data |
|--------|------|------|
| Best model name | Card | Top row from `model_comparison` by roc_auc |
| ROC-AUC comparison | Clustered bar | `model_comparison[model]` vs `[roc_auc]` |
| Recall vs Precision | Scatter | `model_comparison` |
| Metrics table | Table | accuracy, precision, recall, f1, roc_auc |

**Insight callout:**
> Random Forest / XGBoost typically lead on AUC; logistic regression supports coefficient storytelling.

---

## Page 4 — Retention ROI & Explainability

| Visual | Type | Data |
|--------|------|------|
| Est. annual revenue saved | Card | `business_impact` where metric contains "saved" |
| Outreach cost | Card | `business_impact` — Outreach cost |
| Threshold trade-off | Line chart | `threshold_sweep` — precision, recall, f1 vs threshold |
| Top SHAP drivers | Bar chart | `shap_global_importance` top 10 |
| Selected threshold | Card | From `models/churn_threshold.json` (manual or imported) |

---

## Page 5 — CRM Action List

| Visual | Type | Data |
|--------|------|------|
| High-risk customers | Table | `06_high_risk_customers.sql` or rule-based fallback |
| Risk band distribution | Stacked bar | `customer_scores[risk_band]` (Phase 7) |
| Flagged for outreach | Card | Count where flagged_for_outreach = 1 |

**Columns for CRM table:** customer_id, contract, tenure, payment_method, monthly_charges, churn_probability, risk_band

---

## DAX measures

Copy from [`DAX_MEASURES.txt`](DAX_MEASURES.txt) into Power BI Model view.

---

## Build checklist

- [ ] Run notebooks 01–05
- [ ] `python sql/build_analytics_db.py` (includes `customer_scores` if models exist)
- [ ] `python sql/run_all_queries.py` — verify all queries return data
- [ ] Connect Power BI → SQLite → `churnsense_analytics.db`
- [ ] Create 5 pages per layout above
- [ ] Paste DAX from `DAX_MEASURES.txt`
- [ ] Screenshot to `screenshots/dashboard_overview.png`
- [ ] (Optional) Publish to Power BI Service

---

## Interview talking points

1. **SQL layer** decouples analytics from notebooks — reproducible KPIs for stakeholders.
2. **Segment page** ties EDA findings to actionable CRM tiers.
3. **Model page** shows you compare algorithms, not just pick one.
4. **ROI page** connects ML threshold tuning to revenue — not just accuracy.
5. **Action list** closes the loop from insight → outreach.

---

**Next:** Phase 7 — Streamlit app (`app/`) for live churn scoring. Say **"continue Phase 7"**.

After batch scoring in Streamlit, re-run `python sql/build_analytics_db.py` to refresh `customer_scores` for Power BI Page 5.
