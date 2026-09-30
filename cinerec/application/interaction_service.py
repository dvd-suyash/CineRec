import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from cinerec.infrastructure.db.models.activity import Interaction
from cinerec.application.schemas.interaction import InteractionCreate

class InteractionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def track_event(self, user_id: uuid.UUID, payload: InteractionCreate) -> Interaction:
        interaction = Interaction(
            user_id=user_id,
            movie_id=payload.movie_id,
            event_type=payload.event_type,
            session_id=payload.session_id,
            position=payload.position,
            surface=payload.surface,
            event_metadata=payload.metadata
        )
        self.session.add(interaction)
        await self.session.commit()
        await self.session.refresh(interaction)
        return interaction
        
    async def get_recent_events(self, user_id: uuid.UUID, limit: int = 50) -> List[Interaction]:
        stmt = select(Interaction).where(
            Interaction.user_id == user_id
        ).order_by(Interaction.created_at.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
