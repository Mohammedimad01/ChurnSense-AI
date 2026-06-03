-- Rule-based customer segmentation for CRM campaigns
-- Segments align with EDA + SHAP drivers (contract, tenure, payment, value)

SELECT
    customer_id,
    contract,
    tenure,
    payment_method,
    monthly_charges,
    churn,
    CASE
        WHEN contract = 'Month-to-month'
             AND tenure <= 12
             AND monthly_charges >= 70
            THEN '1 — High-Value At-Risk'
        WHEN contract = 'Month-to-month'
             AND tenure <= 12
            THEN '2 — Early-Life MTM'
        WHEN contract = 'Month-to-month'
            THEN '3 — MTM Mature'
        WHEN tenure <= 6
            THEN '4 — Onboarding Window'
        WHEN contract = 'Two year'
             AND churn_flag = 0
            THEN '5 — Loyal Core'
        WHEN payment_method IN ('Electronic check', 'Mailed check')
            THEN '6 — Payment Friction'
        WHEN monthly_charges >= 80
            THEN '7 — Premium Standard'
        ELSE '8 — Stable Base'
    END AS crm_segment,
    churn_flag
FROM customers
ORDER BY crm_segment, monthly_charges DESC;

-- Segment summary for dashboard donut / table
SELECT
    crm_segment,
    COUNT(*)                                     AS customers,
    SUM(churn_flag)                              AS churners,
    ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2)               AS segment_mrr
FROM (
    SELECT
        *,
        CASE
            WHEN contract = 'Month-to-month' AND tenure <= 12 AND monthly_charges >= 70
                THEN '1 — High-Value At-Risk'
            WHEN contract = 'Month-to-month' AND tenure <= 12
                THEN '2 — Early-Life MTM'
            WHEN contract = 'Month-to-month'
                THEN '3 — MTM Mature'
            WHEN tenure <= 6
                THEN '4 — Onboarding Window'
            WHEN contract = 'Two year' AND churn_flag = 0
                THEN '5 — Loyal Core'
            WHEN payment_method IN ('Electronic check', 'Mailed check')
                THEN '6 — Payment Friction'
            WHEN monthly_charges >= 80
                THEN '7 — Premium Standard'
            ELSE '8 — Stable Base'
        END AS crm_segment
    FROM customers
) seg
GROUP BY crm_segment
ORDER BY crm_segment;
