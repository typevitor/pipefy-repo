from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clientes.router import router as clientes_router
from app.core.database import create_tables, engine
from app.pipefy.webhooks.router import router as webhooks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await engine.dispose()


app = FastAPI(title="pipefy-test", lifespan=lifespan)

app.include_router(clientes_router)
app.include_router(webhooks_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
