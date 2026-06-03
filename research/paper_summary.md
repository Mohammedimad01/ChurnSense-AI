# Paper reference - ChurnSense-AI

## Link

- ResearchGate: [Customer churn prediction in telecommunication industry using machine learning models](https://www.researchgate.net/publication/400018499_Customer_churn_prediction_in_telecommunication_industry_using_machine_learning_models)

## Closest peer-reviewed match (empirical study)

Because the ResearchGate page was not fully accessible in this environment, the implementation follows the **same problem domain and methods** as:

- **Chang, V., et al. (2024).** *Prediction of Customer Churn Behavior in the Telecommunication Industry Using Machine Learning Models.* **Algorithms**, 17(6), 231.  
  DOI: [10.3390/a17060231](https://doi.org/10.3390/a17060231)

A **2021 paper with the same title** (Nadeem et al., *Journal of Applied Technology and Innovation*) is a **literature review**, not an end-to-end modeling paper.

## ChurnSense-AI dataset choice

We use the **IBM / Kaggle Telco Customer Churn** dataset (7,043 rows, 21 features) because:

1. It is the industry-standard portfolio dataset for telecom churn.
2. It includes `TotalCharges` cleaning (blank → numeric), which you requested.
3. It supports SQL, dashboards, SHAP, and LR / DT / RF / XGBoost comparison (your planned stack).

The Chang et al. paper uses **Maven Analytics Telecom Churn** (7,043 rows, **38** columns). Analytics logic transfers; column names differ slightly.
