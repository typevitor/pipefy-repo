from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.pipefy.client import PipefyClient
from app.pipefy.dependencies import get_pipefy_client
from app.webhooks import service
from app.webhooks.auth import verify_webhook_secret
from app.webhooks.schemas import WebhookPayload, WebhookResponse

router = APIRouter(prefix="/webhooks/pipefy", tags=["webhooks"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
PipefyDep = Annotated[PipefyClient, Depends(get_pipefy_client)]


@router.post(
    "/card-updated",
    response_model=WebhookResponse,
    dependencies=[Depends(verify_webhook_secret)],
)
async def card_updated(
    payload: WebhookPayload, session: SessionDep, pipefy: PipefyDep
) -> WebhookResponse:
    return await service.processar_webhook(session, payload, pipefy)
