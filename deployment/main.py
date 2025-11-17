from fastapi import FastAPI
from pydantic import BaseModel
import joblib, numpy as np
from prometheus_client import Counter, Histogram, generate_latest
import time

app = FastAPI()

model = joblib.load("models/model.pkl")
scaler = joblib.load("models/scaler.pkl")
encoders = joblib.load("models/encoders.pkl")

REQUEST_COUNT = Counter("request_count", "Total requests")
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", buckets=[0.1,0.5,1,2,5])

class IncomeFeatures(BaseModel):
    features: list

@app.post("/predict")
def predict(data: IncomeFeatures):
    REQUEST_COUNT.inc()
    start = time.time()
    array = np.array([data.features])
    scaled = scaler.transform(array)
    prediction = model.predict(scaled)
    REQUEST_LATENCY.observe(time.time() - start)
    return {"prediction": prediction.tolist()}

@app.get("/metrics")
def metrics():
    return generate_latest()
