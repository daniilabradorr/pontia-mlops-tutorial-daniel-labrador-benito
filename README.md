# Proyecto MLOps – Informe de entrega (Daniel Labrador)

## 1. Contexto del proyecto

Este repositorio es mi implementación del proyecto de **Introducción a DevOps / MLOps** basado en el tutorial de Merlin.  
El objetivo era completar las **tres etapas** del flujo CI/CD:

- `integration`
- `build`
- `deploy` :contentReference[oaicite:0]{index=0}  

Además, se pedía el uso correcto de **GitHub Actions**, **MLflow**, **Azure Storage**, **Azure Container Registry** y **Azure Container Instances**, junto con un README que explique cómo poner todo en marcha.

---

## 2. Estructura del repositorio

A nivel general, el repo está organizado así:

- `src/`
  - `main.py`: script principal de entrenamiento y evaluación del modelo.
  - `data_loader.py`: carga y preprocesado de los datos (encoding + escalado).
- `scripts/`
  - `download_data.py`: descarga `adult.data` y `adult.test` al directorio `data/raw/`.
  - `register_model.py`: registra el modelo entrenado en MLflow usando el `RUN_ID` de la build.
- `unit_tests/`
  - tests de integración sobre la carga de datos, preprocesado y evaluación.
- `model_tests/`
  - `test_model.py`: tests de integración y performance sobre el modelo entrenado.
- `deployment/`
  - `Dockerfile`: imagen de la API de inferencia basada en `mlflow models serve`.
  - `query_model.py`: script de ejemplo para consultar la API.
- `.github/workflows/`
  - `integration.yml`
  - `build.yml`
  - `deploy.yml`
- Otros:
  - `requirements.txt`
  - `pytest.ini`
  - `run_id.txt` (generado en la build)
  - `README.md` (este documento)

---

## 3. Fase 1 – Pipeline de *integration*

### 3.1. Cambios iniciales

Siguiendo el enunciado:

- Actualicé el `.gitignore` para no versionar:
  - entornos virtuales
  - ficheros de datos
  - modelos generados (`models/`)
- Añadí `requirements.txt` con todas las dependencias necesarias.
- Actualicé `MLFLOW_URL` y añadí la variable de entorno `AZURE_STORAGE_CONNECTION_STRING` tanto en local como en GitHub Actions. :contentReference[oaicite:1]{index=1}  
- Probé el código en local ejecutando:

  ```bash
  python scripts/download_data.py
  python src/main.py


### 3.2. `integration.yml` (Workflow de integración)

En `.github/workflows/integration.yml` hice:

* Añadí `workflow_dispatch:` y el trigger sobre `pull_request` a `main`.
* Configuré Python `3.10`.
* En vez de instalar paquetes uno a uno, instalé dependencias desde `requirements.txt`.
* Configuré la ejecución de tests:

```bash
PYTHONPATH=. pytest unit_tests/ \
  --capture=tee-sys \
  --cov=model --cov-report=term --cov-report=html \
  --junitxml=test-results/results.xml > test-results/results.log
```

* El job siempre termina (aunque fallen tests), pero la acción falla si hay errores, como pedía el enunciado.

### 3.3. Branch protection y pruebas

Creé un *ruleset* para la rama `main`:

* No se puede borrar (`restrict deletions`).
* No se permite `force push`.
* Se requieren *status checks* y que la rama esté actualizada.
* Marqué el job de `integration` como *required check*.

Abrí una PR trivial (cambio en el `README`) y comprobé que:

* Se lanza la pipeline.
* Mientras el check no está en verde, no puedo hacer *merge*.

La fase de integración queda completada y funcionando.

---

## 4. Fase 2 – Pipeline de build

### 4.1. Limpieza de datos y modelos

Eliminé del repo cualquier modelo o dataset subido anteriormente:

* `data/raw/*` (se vuelven a descargar con `download_data.py`).
* `models/*` (el modelo se entrena en la build).

Añadí el script `scripts/download_data.py` que descarga:

* `adult.data`
* `adult.test`

### 4.2. Actualización de `register_model.py`

Modifiqué el script para cumplir el enunciado:

* Coge el `RUN_ID` de la variable de entorno `RUN_ID` (ya no lee de `run_id.txt` en la pipeline).
* Usa `MLFLOW_URL` y `EXPERIMENT_NAME` desde variables de entorno.
* Registra el modelo usando:

```python
result = mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name=model_name,
)
```

* Pone el modelo en *Staging* y le asigna el alias `champion`.

### 4.3. Tests de modelo (`model_tests/`)

El fichero `model_tests/test_model.py` hace:

* Comprobar que `models/model.pkl` existe y carga bien.
* Verificar `prediction_shape` y valores de salida `{0, 1}`.
* Para la *accuracy*:

  * Vuelve a cargar `adult.data` y `adult.test`.
  * Reutiliza las funciones de `src/data_loader.py` (`load_data` y `preprocess_data`) para aplicar el mismo preprocesado que durante el entrenamiento.
  * Evalúa la *accuracy* y exige `>= 0.80`.

Esto evita el error original de `could not convert string to float` porque los tests ya no pasan datos crudos al modelo.

### 4.4. Workflow `build.yml`

En `.github/workflows/build.yml`:

**Trigger:**

* `workflow_dispatch:`
* `on: push` a `main`.

**Steps principales:**

1. *Checkout* del repositorio.
2. *Set up* de Python `3.10`.
3. Instalación de dependencias desde `requirements.txt`.
4. `python scripts/download_data.py` para descargar el dataset.
5. `python src/main.py`:

   * Entrena el modelo.
   * Guarda `models/model.pkl`, `models/scaler.pkl` y `models/encoders.pkl`.
   * Registra métricas en MLflow.
   * Guarda el `RUN_ID` de la ejecución en un *output* del job.
6. Ejecución de `pytest model_tests/`.
7. Ejecución de `scripts/register_model.py` usando la variable de entorno `RUN_ID`.

### 4.5. Estado de la fase de build

* En local, los tests de `unit_tests/` y `model_tests/` pasan todos.
* En GitHub Actions, la pipeline **Build Model** termina en verde.
* En MLflow, bajo `Models → merlin-adult-income`, puedo ver:

  * El modelo registrado con varias versiones.
  * Los *artifacts*:

    * `model/model.pkl`
    * `preprocessing/scaler.pkl`
    * `preprocessing/encoders.pkl`.

La fase de *build* queda completada y funcional.

---

## 5. Fase 3 – Pipeline de deploy (estado actual)

### 5.1. `Dockerfile` y carpeta `deployment/`

En `deployment/Dockerfile`:

* Imagen base de Python *slim*.
* Copio `requirements.txt` y los instalo con `pip install --no-cache-dir -r requirements.txt`.
* Copio el script `query_model.py`.
* La imagen está preparada para lanzar la API del modelo con `mlflow models serve`.

### 5.2. *Secrets* y variables en GitHub

He creado en GitHub:

**Secrets:**

* `AZURE_CREDENTIALS`: JSON con `clientId`, `clientSecret`, `tenantId` y `subscriptionId`.
* `ACR_NAME`: nombre del Azure Container Registry.
* `ACR_USERNAME`: usuario de ACR.
* `ACR_PASSWORD`: contraseña/token de ACR.
* `AZURE_RESOURCE_GROUP`: grupo de recursos (por ejemplo `mlflow-rg`).
* `AZURE_STORAGE_CONNECTION_STRING`: cadena completa de conexión a la cuenta de *storage*.

**Variables de Actions:**

* `MODEL_NAME = merlin-adult-income`
* `MODEL_ALIAS = champion`
* `IMAGE_NAME = model-api`
* `AZURE_CONTAINER_NAME = model-api-daniel`
* `AZURE_REGION = eastus`
* `MLFLOW_URL = http://mlflow-9675.eastus.azurecontainer.io:5000/`

### 5.3. Workflow `deploy.yml`

El flujo actual hace:

1. *Login* a Azure con `AZURE_CREDENTIALS`.
2. *Login* a ACR con `ACR_NAME`.
3. Setea `MODEL_URI` en el entorno:

   * `models:/merlin-adult-income@champion`.
4. *Build* de la imagen Docker y *push* a ACR:

   * `ACR_NAME.azurecr.io/model-api`.
5. Creación del *container group* en Azure Container Instances:

   * `--name model-api-daniel`
   * `--image <ACR_NAME>.azurecr.io/model-api`
   * `--os-type Linux`
   * `--ports 8080`
   * `--cpu 1 --memory 2.0`
   * `--environment-variables`:

     * `MODEL_URI`
     * `MLFLOW_TRACKING_URI`
     * `AZURE_STORAGE_CONNECTION_STRING`
6. Espera 90 segundos y ejecuta un *health check*:

```bash
curl --fail http://model-api-daniel-${{ github.run_id }}.eastus.azurecontainer.io:8080/health
```

### 5.4. Problema actual en deploy

* Azure Container Instances crea correctamente el *container group*:

  * El estado aparece como `Running`.
  * Tiene IP pública y FQDN del tipo:

    * `model-api-daniel-<run_id>.eastus.azurecontainer.io:8080`.

Sin embargo, el último paso de la pipeline falla con:

```text
curl: (56) Recv failure: Connection reset by peer
```

* Los logs del contenedor muestran `ExitCode 3` repetidamente (*CrashLoopBackOff*).
* Esto indica que el contenedor arranca, pero el proceso interno se cae (probablemente por un problema al cargar el modelo de MLflow o al acceder al *storage* con la cadena de conexión).

Por tiempo, no he conseguido dejar la API desplegada en Azure respondiendo al endpoint `/health`, aunque en mi máquina local sí he podido:

* Construir la imagen.
* Lanzar el contenedor con `docker run`.
* Consultar la API usando `query_model.py` o `curl`.
