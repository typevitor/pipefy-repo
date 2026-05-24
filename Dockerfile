# ---- builder ----
FROM python:3.12-slim AS builder
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install fastapi "uvicorn[standard]"

# ---- runtime ----
FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN useradd -m appuser
COPY --from=builder /install /usr/local
COPY ./app ./app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
