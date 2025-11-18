import sys
from pathlib import Path
from unittest import mock
import numpy as np

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
API_DIR = ROOT_DIR / "deployment" / "app"
sys.path.append(str(API_DIR))



with mock.patch("joblib.load") as mock_load:
    fake_model = mock.Mock()
    fake_model.predict.return_value = np.array([1])
    fake_scaler = mock.Mock()
    fake_scaler.transform.side_effect = lambda x: x

    mock_load.side_effect = [fake_model, fake_scaler, {}]


    from main import app


client = TestClient(app)


def test_predict_endpoint_returns_200_and_prediction():
    payload = {
        "features": [25, 0, 226802, 7, 14, 0, 9, 0, 4, 0, 2174, 0, 40, 39]
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "prediction" in body
    assert isinstance(body["prediction"], list)


def test_metrics_endpoint_returns_200():
    response = client.get("/metrics")
    assert response.status_code == 200