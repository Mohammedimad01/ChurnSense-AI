-- High-risk customer list for CRM outreach (ML scores)
-- Populate: python sql/generate_customer_scores.py  OR  build_analytics_db.py (auto)
-- Fallback without scores: sql/06b_high_risk_rule_based.sql

SELECT
    c.customer_id,
    c.contract,
    c.tenure,
    c.payment_method,
    c.monthly_charges,
    s.churn_probability,
    s.risk_band,
    s.flagged_for_outreach
FROM customer_scores s
JOIN customers c ON c.customer_id = s.customer_id
WHERE s.flagged_for_outreach = 1
ORDER BY s.churn_probability DESC;

-- Fallback when scores are not yet loaded: rule-based proxy from EDA drivers
-- Uncomment if customer_scores is empty:
/*
SELECT
    customer_id,
    contract,
    tenure,
    payment_method,
    monthly_charges,
    churn_flag AS actual_churn
FROM customers
WHERE contract = 'Month-to-month'
  AND tenure <= 12
  AND payment_method IN ('Electronic check', 'Mailed check')
ORDER BY monthly_charges DESC
LIMIT 200;
*/
