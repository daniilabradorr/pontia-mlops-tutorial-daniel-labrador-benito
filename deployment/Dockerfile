FROM python:3.10-slim
WORKDIR /app
COPY deployment/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY deployment/app/ .
COPY models/ ./models
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
