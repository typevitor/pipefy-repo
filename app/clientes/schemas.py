from pydantic import BaseModel, EmailStr, computed_field, field_validator

from app.core.constants import PRIORIDADE_LABEL, STATUS_LABEL


class ClienteCreate(BaseModel):
    cliente_nome: str
    cliente_email: EmailStr
    tipo_solicitacao: str
    valor_patrimonio: int

    @field_validator("valor_patrimonio")
    @classmethod
    def patrimonio_positivo(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("valor_patrimonio deve ser maior que zero")
        return v


class ClienteRead(BaseModel):
    id: int
    nome: str
    email: str
    tipo_solicitacao: str
    valor_patrimonio: int
    status: int
    prioridade: str | None
    pipefy_card_id: str | None

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def status_label(self) -> str:
        return STATUS_LABEL.get(self.status, str(self.status))

    @computed_field
    @property
    def prioridade_label(self) -> str | None:
        return PRIORIDADE_LABEL.get(self.prioridade) if self.prioridade else None
