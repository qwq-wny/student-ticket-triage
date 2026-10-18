from fastapi.testclient import TestClient

from app.main import app
from app.model import ModelService
from app.schema import TicketRequest
from ml.data_pipeline import build_model

client = TestClient(app)


class FakeModel:
    @property
    def bundle(self):
        return {"metadata": {"version": "test"}}

    def predict(self, ticket):
        return {
            "priority": "urgent",
            "confidence": 0.9,
            "probabilities": {"urgent": 0.9, "normal": 0.1},
            "model_version": "test",
        }


def test_home_and_health():
    assert client.get("/").json() == {"status": "ok"}
    assert client.get("/health").status_code == 200


def test_triage_works(monkeypatch):
    monkeypatch.setattr("app.main.model_service", FakeModel())
    response = client.post(
        "/triage",
        json={
            "text": "production is down",
            "customer_tier": "premium",
            "monthly_revenue": 1000,
        },
    )
    assert response.status_code == 200
    assert response.json()["priority"] == "urgent"


def test_bad_tickets_are_rejected(monkeypatch):
    monkeypatch.setattr("app.main.model_service", FakeModel())
    bad_inputs = [
        {},
        {"text": "hi", "customer_tier": "premium", "monthly_revenue": 10},
        {"text": "hello", "customer_tier": "bad", "monthly_revenue": 10},
        {"text": "hello", "customer_tier": "premium", "monthly_revenue": -1},
        {"text": "hello", "customer_tier": "premium", "monthly_revenue": 10, "extra": 1},
    ]
    for payload in bad_inputs:
        assert client.post("/triage", json=payload).status_code == 422


def test_saved_model_can_predict(tmp_path):
    import joblib
    import pandas as pd

    data = pd.DataFrame(
        {
            "text": ["production outage", "please reset my password"],
            "customer_tier": ["premium", "free"],
            "monthly_revenue": [100, 0],
            "priority": ["urgent", "normal"],
        }
    )
    pipeline = build_model({"max_iter": 100}).fit(data, data["priority"])
    path = tmp_path / "model.joblib"
    joblib.dump(
        {"pipeline": pipeline, "metadata": {"version": "test", "dataset_md5": "0" * 32}}, path
    )

    result = ModelService(path).predict(
        TicketRequest(text="production outage", customer_tier="premium", monthly_revenue=100)
    )
    assert result["priority"] in ("urgent", "normal")
    assert result["probabilities"]
