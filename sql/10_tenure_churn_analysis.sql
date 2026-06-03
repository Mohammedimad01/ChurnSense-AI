-- Tenure-based churn analysis
-- Business question: When in the lifecycle is churn highest?

SELECT
    tenure_group,
    COUNT(*)                                     AS customers,
    SUM(churn_flag)                              AS churners,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(tenure), 1)                        AS avg_tenure_months,
    ROUND(AVG(monthly_charges), 2)               AS avg_monthly_revenue
FROM customers
WHERE tenure_group IS NOT NULL
GROUP BY tenure_group
ORDER BY
    CASE tenure_group
        WHEN '0-6 mo'   THEN 1
        WHEN '7-12 mo'  THEN 2
        WHEN '13-24 mo' THEN 3
        WHEN '25-48 mo' THEN 4
        WHEN '49-72 mo' THEN 5
        WHEN '73+ mo'   THEN 6
        ELSE 7
    END;

-- Raw tenure distribution (for line chart in Power BI)
SELECT
    tenure,
    COUNT(*)                                     AS customers,
    SUM(churn_flag)                              AS churners,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY tenure
HAVING COUNT(*) >= 10
ORDER BY tenure;
