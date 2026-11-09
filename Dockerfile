
FROM python:3.11-slim

WORKDIR /app

# Install backend-only dependencies
COPY requirements-backend.txt .

RUN pip install --no-cache-dir -r requirements-backend.txt

# Copy NLTK resources
COPY nltk_data_minimal/ /usr/share/nltk_data/

# Copy application files
COPY . .

# Configure NLTK resource location
ENV NLTK_DATA=/usr/share/nltk_data

# Create a non-root application user
RUN groupadd --system appuser \
    && useradd --system --gid appuser --home-dir /app appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Container health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" || exit 1

CMD ["uvicorn", "fastapi_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
