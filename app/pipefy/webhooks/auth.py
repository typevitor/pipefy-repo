import secrets

from fastapi import Header, HTTPException

from app.core.config import get_settings


async def verify_webhook_secret(x_webhook_secret: str = Header(default="")) -> None:
    expected = get_settings().pipefy_webhook_secret
    if not secrets.compare_digest(x_webhook_secret.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Webhook secret inválido.")
