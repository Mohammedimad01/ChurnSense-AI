-- Contract × tenure heatmap source (mirrors EDA section 10)
-- Power BI: matrix visual with conditional formatting

SELECT
    contract,
    tenure_group,
    COUNT(*) AS customers,
    SUM(churn_flag) AS churners,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_pct
FROM customers
WHERE tenure_group IS NOT NULL
GROUP BY contract, tenure_group
ORDER BY
    CASE contract
        WHEN 'Month-to-month' THEN 1
        WHEN 'One year' THEN 2
        WHEN 'Two year' THEN 3
        ELSE 4
    END,
    tenure_group;
