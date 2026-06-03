-- Segment churn rates ranked highest to lowest
-- Use in Power BI: bar chart + table visual on Page 2

SELECT
    'Contract' AS segment_type,
    contract AS segment_value,
    customers,
    churners,
    churn_rate_pct
FROM churn_by_contract

UNION ALL

SELECT
    'Payment Method',
    payment_method,
    customers,
    churners,
    churn_rate_pct
FROM churn_by_payment

UNION ALL

SELECT
    'Tenure Band',
    tenure_group,
    customers,
    churners,
    churn_rate_pct
FROM churn_by_tenure_band

UNION ALL

SELECT
    'Charge Band',
    charge_group,
    customers,
    churners,
    churn_rate_pct
FROM churn_by_charge_band

ORDER BY churn_rate_pct DESC;
