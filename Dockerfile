FROM python:3.13-slim
# Ping высокий 
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
COPY . .
RUN mkdir -p src/models/db_models && chmod -R 777 src/models/db_models
EXPOSE 5000
CMD ["mlflow", "ui", "--backend-store-uri", "sqlite:///src/models/db_models/mlflow.db", "--host", "0.0.0.0", "--port", "5000"]
