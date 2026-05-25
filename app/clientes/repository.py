from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clientes.models import Cliente


async def insert(
    session: AsyncSession,
    nome: str,
    email: str,
    tipo_solicitacao: str,
    valor_patrimonio: int,
) -> Cliente:
    cliente = Cliente(
        nome=nome,
        email=email,
        tipo_solicitacao=tipo_solicitacao,
        valor_patrimonio=valor_patrimonio,
        status="Aguardando Análise",
    )
    session.add(cliente)
    await session.commit()
    await session.refresh(cliente)
    return cliente


async def get_by_email(session: AsyncSession, email: str) -> Cliente | None:
    result = await session.execute(select(Cliente).where(Cliente.email == email))
    return result.scalar_one_or_none()


async def update_pipefy_card_id(
    session: AsyncSession, cliente: Cliente, card_id: str
) -> None:
    cliente.pipefy_card_id = card_id
    await session.commit()


async def update_status_prioridade(
    session: AsyncSession, cliente: Cliente, status: str, prioridade: str
) -> Cliente:
    cliente.status = status
    cliente.prioridade = prioridade
    await session.commit()
    await session.refresh(cliente)
    return cliente
