import os, mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri(os.getenv("MLFLOW_URL"))  # antes estaba hardcodeado

# Obtener run_id desde una variable de entorno RUN_ID
run_id = os.getenv("RUN_ID")
if not run_id:
    with open("run_id.txt") as f:
        run_id = f.read().strip()

client = MlflowClient()
model_name  = os.getenv("MODEL_NAME", "no_name")
result = mlflow.register_model(model_uri=f"runs:/{run_id}/models/model.pkl", name=model_name)

# Transicionar a Staging y establecer alias
client.transition_model_version_stage(name=model_name, version=result.version, stage="Staging")
client.set_registered_model_alias(model_name, os.getenv("MODEL_ALIAS", "champion"), result.version)
