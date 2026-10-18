import pandas as pd
import pytest

from ml.data_pipeline import build_model, build_preprocessor, validate_training_frame


@pytest.fixture
def data():
    return pd.DataFrame(
        {
            "text": ["production outage", "reset my password", "add dark mode"],
            "customer_tier": ["premium", "free", "standard"],
            "monthly_revenue": [1000, 0, 10],
            "priority": ["urgent", "normal", "low"],
        }
    )


def test_preprocessing_works(data):
    features = build_preprocessor().fit_transform(data)
    assert features.shape[0] == 3
    assert features.shape[1] > 3


def test_preprocessing_allows_new_customer_tier(data):
    processor = build_preprocessor().fit(data)
    data["customer_tier"] = "unknown"
    assert processor.transform(data).shape[0] == 3


def test_model_can_fit_and_predict(data):
    model = build_model({"max_iter": 100}).fit(data, data["priority"])
    assert model.predict(data.head(1)).shape == (1,)


def test_bad_training_data_is_rejected(data):
    bad_versions = [
        data.drop(columns="text"),
        data.assign(text=[None, None, None]),
        data.assign(priority=["wrong", "normal", "low"]),
        data.iloc[0:0],
    ]
    for bad_data in bad_versions:
        with pytest.raises(ValueError):
            validate_training_frame(bad_data)
