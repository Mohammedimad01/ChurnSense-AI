-- Rule-based high-risk list (works without ML scores)
-- Use when customer_scores table is empty — mirrors EDA red-account logic

SELECT
    customer_id,
    contract,
    tenure,
    payment_method,
    monthly_charges,
    total_charges,
    churn,
    churn_flag,
    'Rule: MTM + tenure<=12 + manual pay' AS risk_reason
FROM customers
WHERE contract = 'Month-to-month'
  AND tenure <= 12
  AND payment_method IN ('Electronic check', 'Mailed check')
ORDER BY monthly_charges DESC
LIMIT 200;
