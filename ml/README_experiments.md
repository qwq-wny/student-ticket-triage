# MLflow experiments

Two experiments were run locally with MLflow. The code used for both was commit `bffc61a3d544a5a003d60b33fdb706f2e9bea3da`.

## 1. Baseline

- Dataset: v1
- Run: `d39f022911f7464182bee50f6511c58a`
- C: `1.0`
- class_weight: none
- Accuracy: `0.8158`
- Macro F1: `0.8061`

## 2. Improved

- Dataset: v2
- Run: `dd502770a1a7442ea92e14c2d307190b`
- C: `2.0`
- class_weight: `balanced`
- Accuracy: `1.0`
- Macro F1: `1.0`

## Why v2 is the production model

Macro F1 is used because it shows how all four classes perform, not just the most common class. The v2 dataset is balanced and cleaned, so its model is saved in `ml/artifacts/v2_logistic_regression.joblib` and used by the API.

The perfect score is expected because the toy data is generated from clear text templates. Real production data would probably give a lower score.
