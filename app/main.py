from fastapi import FastAPI

app = FastAPI(title="pipefy-test")


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}
