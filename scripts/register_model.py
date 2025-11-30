import os
from pathlib import Path

import mlflow
from mlflow.tracking import MlflowClient


#MLflow desde variables de entorno
MLFLOW_URL = os.environ["MLFLOW_URL"]
EXPERIMENT_NAME = os.environ["EXPERIMENT_NAME"]
RUN_ID = os.environ["RUN_ID"]
MODEL_NAME = os.getenv("MODEL_NAME", "no_name")

mlflow.set_tracking_uri(MLFLOW_URL)
mlflow.set_experiment(EXPERIMENT_NAME)
client = MlflowClient()

# modelo dentro de los artefactos del run
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "models"
model_artifact_path = MODEL_DIR / "model.pkl"

#el modelo en MLflow
result = mlflow.register_model(
    model_uri=f"runs:/{RUN_ID}/{model_artifact_path}",
    name=MODEL_NAME,
)

#el modelo a Staging y marcar alias "champion"
client.transition_model_version_stage(
    name=MODEL_NAME,
    version=result.version,
    stage="Staging",
)

client.set_registered_model_alias(MODEL_NAME, "champion", result.version)
