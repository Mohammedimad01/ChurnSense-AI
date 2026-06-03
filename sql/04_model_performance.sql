-- ML model comparison for data science / stakeholder review
-- Power BI: clustered bar chart (model vs roc_auc, recall, f1)

SELECT
    model,
    ROUND(accuracy, 4)        AS accuracy,
    ROUND(precision_score, 4) AS precision_score,
    ROUND(recall, 4)          AS recall,
    ROUND(f1, 4)              AS f1,
    ROUND(roc_auc, 4)         AS roc_auc
FROM model_comparison
ORDER BY roc_auc DESC;
