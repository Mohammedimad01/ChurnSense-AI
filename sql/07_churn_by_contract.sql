-- Churn rate by contract type
-- Business question: Which contract types drive attrition?

SELECT
    contract,
    COUNT(*)                                              AS customers,
    SUM(churn_flag)                                       AS churners,
    COUNT(*) - SUM(churn_flag)                            AS retained,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2)          AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2)                        AS avg_monthly_revenue,
    ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 2)
        AS monthly_revenue_lost
FROM customers
GROUP BY contract
ORDER BY churn_rate_pct DESC;
