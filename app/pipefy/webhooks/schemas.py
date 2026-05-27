from datetime import datetime

from pydantic import BaseModel, EmailStr


class WebhookPayload(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: datetime


class WebhookResponse(BaseModel):
    status: str
    prioridade: str | None = None
    prioridade_label: str | None = None
