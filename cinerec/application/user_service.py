import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from cinerec.infrastructure.db.models import User, UserIdentity, UserProfile

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        stmt = select(User).join(UserIdentity).where(
            UserIdentity.provider == "google",
            UserIdentity.provider_subject == google_id,
            User.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_user_from_google(self, google_id: str, email: str, name: str, picture: Optional[str] = None) -> User:
        user = User(
            display_name=name,
            avatar_url=picture,
            onboarding_status="COMPLETED"
        )
        self.session.add(user)
        await self.session.flush() # flush to get user.id

        identity = UserIdentity(
            user_id=user.id,
            provider="google",
            provider_subject=google_id,
            email=email,
            email_verified=True
        )
        self.session.add(identity)

        profile = UserProfile(
            user_id=user.id
        )
        self.session.add(profile)
        
        await self.session.commit()
        await self.session.refresh(user)
        return user
