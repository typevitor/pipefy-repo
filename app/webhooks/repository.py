from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.webhooks.models import WebhookEvent


async def get_event(session: AsyncSession, event_id: str) -> WebhookEvent | None:
    result = await session.execute(
        select(WebhookEvent).where(WebhookEvent.event_id == event_id)
    )
    return result.scalar_one_or_none()


async def insert_event(session: AsyncSession, event_id: str) -> WebhookEvent:
    event = WebhookEvent(event_id=event_id)
    session.add(event)
    await session.commit()
    return event
