import os
import pytest
import joblib
import numpy as np
from sklearn.metrics import accuracy_score

from src.data_loader import load_data, preprocess_data


def test_model_loading():
    model_path = "models/model.pkl"
    assert os.path.exists(model_path), f"Model file not found at {model_path}"
    try:
        _ = joblib.load(model_path)
    except Exception as e:
        pytest.fail(f"Failed to load model: {e}")


def test_prediction_shape():
    model = joblib.load("models/model.pkl")
    sample_input = np.random.rand(5, model.n_features_in_)
    predictions = model.predict(sample_input)
    assert predictions.shape == (5,), f"Expected predictions of shape (5,), got {predictions.shape}"


def test_prediction_values():
    model = joblib.load("models/model.pkl")
    sample_input = np.random.rand(5, model.n_features_in_)
    predictions = model.predict(sample_input)
    assert set(predictions).issubset(
        {0, 1}
    ), f"Predictions contain unexpected classes: {set(predictions)}"


def test_model_accuracy():
    """
    Comprobamos la accuracy usando el MISMO preprocesado que en src/main.py.
    Usamos load_data + preprocess_data, que ya hacen limpieza, encoding y escalado.
    """
    train_path = "data/raw/adult.data"
    test_path = "data/raw/adult.test"

    train_df, test_df = load_data(train_path, test_path)

    #aplica el prepocesado
    X_train, X_test, y_train, y_test, scaler, label_encoders = preprocess_data(
        train_df, test_df
    )

    #cargo le modelo entrenado
    model = joblib.load("models/model.pkl")

    predictions = model.predict(X_test)

    #compruebo que la accuracy es razonabel
    accuracy = accuracy_score(y_test, predictions)
    assert accuracy >= 0.80, f"Model accuracy below expected threshold: {accuracy:.2f}"
