# MLflow experiments

Two experiments were run locally with MLflow. The code used for both was commit `90cca78b0a2deff4f7229814e2e8c2b87a1f169c`.

## 1. Baseline

- Dataset: v1
- Run: `3d6540acd515464fa409efa9c82550b8`
- C: `1.0`
- class_weight: none
- Accuracy: `0.8158`
- Macro F1: `0.8061`

## 2. Improved

- Dataset: v2
- Run: `e38a420449c441298a0e4abc002b4787`
- C: `2.0`
- class_weight: `balanced`
- Accuracy: `1.0`
- Macro F1: `1.0`

## Why v2 is the production model

Macro F1 is used because it shows how all four classes perform, not just the most common class. The v2 dataset is balanced and cleaned, so its model is saved in `ml/artifacts/v2_logistic_regression.joblib` and used by the API.

The perfect score is expected because the toy data is generated from clear text templates. Real production data would probably give a lower score.

