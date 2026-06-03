-- High-value customer analysis (top 25% by monthly charges)
-- SQLite-compatible — uses OFFSET for 75th percentile threshold

WITH mrc_threshold AS (
    SELECT monthly_charges AS p75_mrc
    FROM customers
    ORDER BY monthly_charges
    LIMIT 1 OFFSET (
        SELECT CAST(COUNT(*) * 0.75 AS INTEGER) FROM customers
    )
),
tagged AS (
    SELECT
        c.*,
        CASE
            WHEN c.monthly_charges >= (SELECT p75_mrc FROM mrc_threshold) THEN 'High Value (Top 25% MRC)'
            ELSE 'Standard Value'
        END AS value_tier
    FROM customers c
)
SELECT
    value_tier,
    COUNT(*)                                     AS customers,
    SUM(churn_flag)                              AS churners,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2)               AS avg_monthly_revenue,
    ROUND(SUM(monthly_charges) * 12, 2)          AS annual_revenue_base
FROM tagged
GROUP BY value_tier
ORDER BY churn_rate_pct DESC;

-- Detail: high-value customers who churned (revenue at risk)
SELECT
    customer_id,
    contract,
    tenure,
    payment_method,
    monthly_charges,
    total_charges,
    churn
FROM tagged
WHERE value_tier = 'High Value (Top 25% MRC)'
  AND churn_flag = 1
ORDER BY monthly_charges DESC
LIMIT 50;
