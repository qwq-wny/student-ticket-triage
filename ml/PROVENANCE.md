# Provenance

- Model used by API: `ml/artifacts/v2_logistic_regression.joblib`
- Dataset: `data/tickets_v2.csv`
- DVC hash: `a1640c8c6041889f71eb384b8585853f`
- Training commit: `bffc61a3d544a5a003d60b33fdb706f2e9bea3da`
- MLflow run: `dd502770a1a7442ea92e14c2d307190b`
- Python: 3.12
- Main libraries: FastAPI, pandas, scikit-learn, MLflow, DVC

To reproduce:

```bash
python ml/scripts/build_dataset.py v1
python ml/scripts/build_dataset.py v2
python -m ml.train --config ml/configs/baseline.json
python -m ml.train --config ml/configs/improved.json
```
