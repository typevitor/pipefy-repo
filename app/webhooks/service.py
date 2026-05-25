import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.clientes import repository as clientes_repo
from app.pipefy.client import PipefyClient
from app.webhooks import repository as webhooks_repo
from app.webhooks.schemas import WebhookPayload, WebhookResponse

logger = logging.getLogger(__name__)

PRIORIDADE_ALTA_THRESHOLD = 20_000_000  # R$ 200.000,00 em centavos


async def processar_webhook(
    session: AsyncSession, payload: WebhookPayload, pipefy: PipefyClient
) -> WebhookResponse:
    existing = await webhooks_repo.get_event(session, payload.event_id)
    if existing:
        return WebhookResponse(status="already_processed")

    cliente = await clientes_repo.get_by_email(session, str(payload.cliente_email))
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    prioridade = (
        "prioridade_alta"
        if cliente.valor_patrimonio >= PRIORIDADE_ALTA_THRESHOLD
        else "prioridade_normal"
    )

    if cliente.pipefy_card_id:
        try:
            await pipefy.update_card_fields(
                card_id=cliente.pipefy_card_id,
                status="Processado",
                prioridade=prioridade,
            )
        except Exception:
            logger.exception(
                "Falha ao atualizar card %s no Pipefy", cliente.pipefy_card_id
            )

    await clientes_repo.update_status_prioridade(session, cliente, "Processado", prioridade)
    try:
        await webhooks_repo.insert_event(session, payload.event_id)
    except IntegrityError:
        await session.rollback()
        return WebhookResponse(status="already_processed")

    return WebhookResponse(status="processed", prioridade=prioridade)
