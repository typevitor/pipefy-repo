from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clientes import service
from app.clientes.schemas import ClienteCreate, ClienteRead
from app.core.database import get_session
from app.pipefy.client import PipefyClient
from app.pipefy.dependencies import get_pipefy_client

router = APIRouter(prefix="/clientes", tags=["clientes"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
PipefyDep = Annotated[PipefyClient, Depends(get_pipefy_client)]


@router.post("", response_model=ClienteRead, status_code=201)
async def criar_cliente(
    payload: ClienteCreate, session: SessionDep, pipefy: PipefyDep
) -> ClienteRead:
    return await service.criar_cliente(session, payload, pipefy)


@router.get("/{email}", response_model=ClienteRead)
async def get_cliente(email: str, session: SessionDep) -> ClienteRead:
    return await service.get_cliente(session, email)
