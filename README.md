# pipefy-test

Esqueleto mínimo de uma API FastAPI que retorna `{"status": "ok"}`.

## Rodar localmente (uv)

```bash
uv sync
uv run uvicorn app.main:app --reload
```

- API: http://localhost:8000/ → `{"status":"ok"}`
- Docs (Swagger): http://localhost:8000/docs

## Rodar com Docker

```bash
docker compose up --build
```

- API: http://localhost:8000/
