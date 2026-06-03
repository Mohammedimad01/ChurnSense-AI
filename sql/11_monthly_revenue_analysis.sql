-- Monthly revenue analysis by segment
-- Business question: Where is revenue concentrated and where is it leaking?

SELECT
    charge_group,
    COUNT(*)                                     AS customers,
    ROUND(SUM(monthly_charges), 2)               AS total_monthly_revenue,
    ROUND(AVG(monthly_charges), 2)               AS avg_monthly_revenue,
    SUM(churn_flag)                              AS churners,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 2)
        AS monthly_revenue_lost
FROM customers
WHERE charge_group IS NOT NULL
GROUP BY charge_group
ORDER BY total_monthly_revenue DESC;

-- Revenue by contract (retention vs revenue trade-off)
SELECT
    contract,
    COUNT(*)                                     AS customers,
    ROUND(SUM(monthly_charges), 2)               AS total_monthly_revenue,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(
        SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END) * 12,
        2
    )                                            AS annual_revenue_at_risk
FROM customers
GROUP BY contract
ORDER BY annual_revenue_at_risk DESC;

-- Portfolio revenue summary
SELECT
    ROUND(SUM(monthly_charges), 2)               AS total_mrr,
    ROUND(SUM(monthly_charges) * 12, 2)          AS total_arr,
    ROUND(AVG(monthly_charges), 2)               AS avg_mrc,
    ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 2)
        AS mrr_lost_to_churn,
    ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END) * 12, 2)
        AS arr_at_risk
FROM customers;
