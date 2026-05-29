FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN pip install --no-cache-dir \
    "fastapi>=0.115" \
    "uvicorn[standard]>=0.32" \
    "sqlalchemy>=2.0" \
    "aiosqlite>=0.20" \
    "pydantic[email]>=2.0" \
    "pydantic-settings>=2.0" \
    "gql[httpx]>=3.5" \
    "pytest>=8.0" \
    "pytest-asyncio>=0.24" \
    "anyio[trio]>=4.0"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
