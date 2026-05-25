from pydantic import BaseModel, EmailStr, field_validator


class ClienteCreate(BaseModel):
    cliente_nome: str
    cliente_email: EmailStr
    tipo_solicitacao: str
    valor_patrimonio: int  # centavos — R$ 250.000,00 → 25000000

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
    valor_patrimonio: int  # centavos
    status: str
    prioridade: str | None
    pipefy_card_id: str | None

    model_config = {"from_attributes": True}
