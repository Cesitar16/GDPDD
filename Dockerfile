FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY docker-requirements.txt .
RUN pip install --no-cache-dir -r docker-requirements.txt
RUN pip install --no-cache-dir --no-deps xgboost==3.2.0

COPY app.py .
COPY .streamlit/ .streamlit/
COPY src/ src/
COPY outputs/models/heart_disease_pipeline.joblib outputs/models/heart_disease_pipeline.joblib
COPY outputs/tables/shap_importancia_global.csv outputs/tables/shap_importancia_global.csv
COPY data/processed/heart_unique.csv data/processed/heart_unique.csv

EXPOSE 8000 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
