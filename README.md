# Student Support-Ticket Triage App

This is a small machine-learning project. The API reads a support ticket and predicts one priority: `urgent`, `high`, `normal`, or `low`.

The model is a scikit-learn logistic regression trained on text, customer tier, and monthly revenue. The data is synthetic, so there is no private customer information.

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Then open <http://127.0.0.1:8000/docs>.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"production is down\",\"customer_tier\":\"premium\",\"monthly_revenue\":1000}"
```

## Tests

```bash
ruff format --check .
ruff check .
pytest
```

## Data and training

There are two small DVC versions:

- `data/tickets_v1.csv.dvc`: 150 rows, imbalanced, some noisy labels
- `data/tickets_v2.csv.dvc`: 240 rows, balanced and cleaned

The raw CSV files are not stored in Git. If you have Azure DVC storage configured, run:

```bash
dvc pull
```

You can also recreate the toy data:

```bash
python ml/scripts/build_dataset.py v1
python ml/scripts/build_dataset.py v2
```

Train the two MLflow experiments:

```bash
pip install -r requirements-ml.txt
python -m ml.train --config ml/configs/baseline.json
python -m ml.train --config ml/configs/improved.json
```

Run history is written to `ml/mlruns`. See `ml/README_experiments.md` for the two runs and metrics.

## Git and CI/CD

Branch path:

```text
feature/* -> dev -> staging -> main
```

GitHub Actions:

- PR to `dev`, `staging`, or `main`: format check, Ruff, tests, Docker build
- Push to `staging`: create a staging `.env` from secrets and build a staging image
- Push to `main`: create a production `.env` from secrets and build a production image

The project does not deploy anywhere. It only builds environment images, as required by the assignment.

## Docker

Docker is not run on this computer. GitHub Actions builds the image in the cloud:

```bash
docker build -t ticket-triage .
docker run --rm -p 8000:8000 ticket-triage
```

CI status: checked automatically by GitHub Actions.

