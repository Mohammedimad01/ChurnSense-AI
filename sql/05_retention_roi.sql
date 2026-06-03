-- Retention ROI and threshold sensitivity (Phase 5 exports)
-- Power BI Page 4: executive ROI card + line chart

-- Business impact summary (tuned threshold scenario)
SELECT metric, value
FROM business_impact
ORDER BY metric;

-- Threshold sweep for precision/recall trade-off chart
SELECT
    threshold,
    ROUND(precision_score, 4) AS precision_score,
    ROUND(recall, 4)          AS recall,
    ROUND(f1, 4)              AS f1,
    ROUND(flagged_pct * 100, 2) AS flagged_pct
FROM threshold_sweep
ORDER BY threshold;

-- Top SHAP drivers for feature importance visual
SELECT feature, ROUND(mean_abs_shap, 6) AS mean_abs_shap
FROM shap_global_importance
ORDER BY mean_abs_shap DESC
LIMIT 15;
