# Provenance

- Model used by API: `ml/artifacts/v2_logistic_regression.joblib`
- Dataset: `data/tickets_v2.csv`
- DVC hash: `a1640c8c6041889f71eb384b8585853f`
- Training commit: `90cca78b0a2deff4f7229814e2e8c2b87a1f169c`
- MLflow run: `e38a420449c441298a0e4abc002b4787`
- Python: 3.12
- Main libraries: FastAPI, pandas, scikit-learn, MLflow, DVC

To reproduce:

```bash
python ml/scripts/build_dataset.py v1
python ml/scripts/build_dataset.py v2
python -m ml.train --config ml/configs/baseline.json
python -m ml.train --config ml/configs/improved.json
```

