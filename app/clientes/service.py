import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.clientes import repository as repo
from app.clientes.schemas import ClienteCreate, ClienteRead
from app.pipefy.client import PipefyClient

logger = logging.getLogger(__name__)


async def get_cliente(session: AsyncSession, email: str) -> ClienteRead:
    cliente = await repo.get_by_email(session, email)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return ClienteRead.model_validate(cliente)


async def criar_cliente(
    session: AsyncSession, payload: ClienteCreate, pipefy: PipefyClient
) -> ClienteRead:
    existing = await repo.get_by_email(session, str(payload.cliente_email))
    if existing:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")

    cliente = await repo.insert(
        session,
        nome=payload.cliente_nome,
        email=str(payload.cliente_email),
        tipo_solicitacao=payload.tipo_solicitacao,
        valor_patrimonio=payload.valor_patrimonio,
    )

    try:
        card_id = await pipefy.create_card(
            nome=payload.cliente_nome,
            email=str(payload.cliente_email),
            valor_patrimonio=payload.valor_patrimonio,
        )
        await repo.update_pipefy_card_id(session, cliente, card_id)
        cliente.pipefy_card_id = card_id
    except Exception:
        logger.exception("Falha ao criar card no Pipefy para %s", payload.cliente_email)

    return ClienteRead.model_validate(cliente)
