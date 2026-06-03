-- Churn rate by payment method
-- Business question: Does manual payment increase churn?

SELECT
    payment_method,
    COUNT(*)                                     AS customers,
    SUM(churn_flag)                              AS churners,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(tenure), 1)                        AS avg_tenure_months,
    ROUND(AVG(monthly_charges), 2)               AS avg_monthly_revenue
FROM customers
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;
