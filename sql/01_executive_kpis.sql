-- Executive KPI snapshot for retention leadership
-- Expected output: single row with portfolio health metrics

SELECT
    COUNT(*)                                              AS total_customers,
    SUM(churn_flag)                                       AS total_churners,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2)          AS overall_churn_rate_pct,
    ROUND(AVG(monthly_charges), 2)                        AS avg_monthly_revenue,
    ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 2)
        AS monthly_revenue_lost_to_churn,
    ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END) * 12, 2)
        AS annual_revenue_at_risk,
    SUM(CASE WHEN contract = 'Month-to-month' THEN 1 ELSE 0 END)
        AS mtm_customers,
    ROUND(
        100.0 * SUM(CASE WHEN contract = 'Month-to-month' AND churn_flag = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN contract = 'Month-to-month' THEN 1 ELSE 0 END), 0),
        2
    )                                                     AS mtm_churn_rate_pct
FROM customers;
