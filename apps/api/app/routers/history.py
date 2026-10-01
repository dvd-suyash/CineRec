import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.dependencies.auth import get_current_user
from apps.api.app.dependencies.db import get_db_session
from cinerec.core.api import DataResponse
from cinerec.infrastructure.db.models.activity import ViewingHistory, Watchlist
from cinerec.infrastructure.db.models.user import User

router = APIRouter()

@router.post("/movies/{movie_id}")
async def mark_as_watched(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # Check if already in history
    stmt = select(ViewingHistory).where(ViewingHistory.user_id == current_user.id, ViewingHistory.movie_id == movie_id)
    result = await db.execute(stmt)
    entry = result.scalars().first()

    if entry:
        entry.status = "COMPLETED"
        entry.completed_at = datetime.now(timezone.utc)
    else:
        entry = ViewingHistory(
            user_id=current_user.id,
            movie_id=movie_id,
            status="COMPLETED",
            completed_at=datetime.now(timezone.utc)
        )
        db.add(entry)

    # Remove from watchlist if present
    stmt_wl = select(Watchlist).where(Watchlist.user_id == current_user.id, Watchlist.movie_id == movie_id)
    result_wl = await db.execute(stmt_wl)
    wl_entry = result_wl.scalars().first()
    if wl_entry:
        await db.delete(wl_entry)

    await db.commit()

    return DataResponse(data={"status": "success"})
