# MLOps – MLflow + GitHub Actions + Azure

Este repositorio contiene la solución al ejercicio de introducción a DevOps / MLOps:

- Entrenamiento de un modelo de clasificación (Adult Income).
- Registro del modelo en MLflow.
- Construcción de una imagen Docker con una API FastAPI.
- Despliegue en Azure Container Instances mediante GitHub Actions.

> ⚠️ **Nota importante sobre MLflow**  
> La URL de MLflow proporcionada en el enunciado (`http://57.151.65.76:5000`) **no responde actualmente** (timeout tanto desde navegador como desde GitHub Actions).  
> Por este motivo, el workflow `build` falla en el paso de entrenamiento/registro al intentar conectarse al servidor de MLflow remoto.  
> El resto del flujo (código, tests, workflows, Docker y Azure) está implementado y listo para funcionar en cuanto el servidor vuelva a estar disponible **sin necesidad de cambios en el repositorio**.

---

## Estructura del proyecto

```bash
.
├── src/
│   ├── data_loader.py
│   ├── evaluate.py
│   ├── model.py
│   └── main.py           # Entrenamiento + logging en MLflow
├── scripts/
│   └── register_model.py # Registro del modelo en MLflow (Staging + alias)
├── deployment/
│   ├── app/
│   │   └── main.py       # API FastAPI (/predict, /metrics)
│   ├── requirements.txt  # Dependencias de la API
│   └── Dockerfile        # Imagen de inferencia
├── tests/
│   ├── test_data_loader.py
│   ├── test_model.py
│   ├── test_evaluate.py
│   └── test_api.py       # Tests de la API FastAPI con TestClient
├── .github/
│   └── workflows/
│       ├── integration.yml
│       ├── build.yml
│       └── deploy.yml
└── requirements.txt      # Dependencias de entrenamiento
```

## Pipelines implementadas

integration.yml: ejecuta los tests automáticos con pytest.

build.yml: entrena el modelo, evalúa y registra en MLflow.

deploy.yml: construye la imagen Docker y despliega en Azure.

Todos los secretos como MLFLOW_URL, AZURE_CREDENTIALS, ACR_USERNAME, etc. están definidos en los Secrets de GitHub para mayor seguridad.

## Despliegue en Azure

El servicio se despliega como un contenedor Docker en Azure Container Instances. Se exponen dos endpoints:

POST /predict: recibe un JSON y devuelve la clase predicha (>50K o <=50K).

GET /metrics: expone métricas para Prometheus.

Ejemplo de petición:

curl -X POST "http://<IP_CONTAINER>/predict" \
     -H "Content-Type: application/json" \
     -d '{"data": [[39, "State-gov", 77516, "Bachelors", 13, "Never-married", "Adm-clerical", "Not-in-family", "White", "Male", 2174, 0, 40, "United-States"]]}'

Respuesta:

{"prediction": ["<=50K"]}