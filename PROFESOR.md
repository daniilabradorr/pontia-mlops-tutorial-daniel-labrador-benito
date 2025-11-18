# README – API Testeada Localmente

Este archivo README complementario explica cómo se ha verificado la funcionalidad de la API de predicción de ingresos desarrollada en FastAPI.

En lugar de hacerle un video a usted profesor le hago un readme mas simple, sencillo y rapido

---

## 1. Entorno local

Se ha probado la API ejecutando el servidor localmente:

```bash
cd deployment/app
uvicorn main:app --reload
```

Esto inicia la API en `http://127.0.0.1:8000`

---

## 2. Endpoint `/predict`

Se envió la siguiente petición con `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"data": [[39, "State-gov", 77516, "Bachelors", 13, "Never-married", "Adm-clerical", "Not-in-family", "White", "Male", 2174, 0, 40, "United-States"]]}'
```

La respuesta recibida fue:

```json
{"prediction": ["<=50K"]}
```

---

## 3. Endpoint `/metrics`

Está disponible para Prometheus en `http://127.0.0.1:8000/metrics`, retornando:

```
# HELP api_requests_total Total number of prediction requests
# TYPE api_requests_total counter
api_requests_total 1
```

---

## 4. Observación sobre MLflow

**IMPORTANTE**: El servicio de tracking remoto de MLflow no se pudo validar desde GitHub Actions debido a un fallo con la URL proporcionada por Azure. La variable `MLFLOW_URL` apunta a una dirección pública generada, pero al intentar conectarse, da error 403/Timeout. Esto ha sido documentado y se explica en el README principal.

---

## 5. Conclusión

Aunque el tracking remoto con MLflow no pudo completarse por problemas ajenos al código, el flujo completo ha sido verificado localmente. La API está funcional, el modelo responde adecuadamente, y todo el proyecto cumple con los requisitos funcionales del ejercicio.

## EJEMPLO REAL
le copio tal cual el ejemplo de uno pytest general de los últimos que realice donde se ve que funciona, incluso le dejo que me salio un warning.

(venv) PS C:\Users\danie\OneDrive\Desktop\ejerciciofinDevOps\pontia-mlops-tutorial> pytest
====================================== test session starts ======================================
platform win32 -- Python 3.13.5, pytest-9.0.1, pluggy-1.6.0
rootdir: C:\Users\danie\OneDrive\Desktop\ejerciciofinDevOps\pontia-mlops-tutorial
configfile: pytest.ini
plugins: anyio-4.11.0
collected 7 items                                                                                

tests\test_api.py ..                                                                       [ 28%]
tests\test_data_loader.py ..                                                               [ 57%]
tests\test_evaluate.py .                                                                   [ 71%]
tests\test_model.py ..                                                                     [100%]

======================================= warnings summary ======================================== 
================================= 7 passed, 1 warning in 1.92s