FROM python:3.12-slim

WORKDIR /app

# D'abord les dépendances seules : tant que requirements.txt ne change pas,
# Docker réutilise cette étape (longue) sans la refaire
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# Ensuite le code, qui change souvent
COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
