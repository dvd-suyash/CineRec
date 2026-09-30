import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from cinerec.infrastructure.db.models.memory import Memory, MemoryEvidence

class MemoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def add_memory_evidence(
        self,
        user_id: uuid.UUID,
        subject: str,
        memory_type: str,
        polarity: str,
        source: str,
        evidence_type: str,
        value: Optional[dict] = None,
        weight: float = 1.0,
        conversation_id: Optional[uuid.UUID] = None
    ) -> Memory:
        """
        Record evidence and extract memory.
        If a similar active memory exists, we update evidence and status.
        Otherwise we create a new CANDIDATE memory.
        """
        # Find existing memory by subject/type
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.subject == subject,
            Memory.memory_type == memory_type,
            Memory.status.in_(["ACTIVE", "VALIDATED", "CANDIDATE"])
        )
        result = await self.session.execute(stmt)
        memory = result.scalars().first()
        
        now = datetime.now(timezone.utc)
        
        if not memory:
            # Create new memory
            status = "ACTIVE" if source == "USER_EXPLICIT" else "CANDIDATE"
            confidence = 1.0 if source == "USER_EXPLICIT" else 0.4
            
            memory = Memory(
                user_id=user_id,
                memory_type=memory_type,
                subject=subject,
                value=value,
                polarity=polarity,
                confidence=confidence,
                source=source,
                status=status,
                evidence_count=1,
                last_evidence_at=now
            )
            self.session.add(memory)
            await self.session.flush()
        else:
            # Update existing
            memory.evidence_count += 1
            memory.last_evidence_at = now
            # Recalculate confidence
            if memory.confidence < 1.0:
                memory.confidence = min(0.9, float(memory.confidence) + (0.1 * weight))
            if memory.status == "CANDIDATE" and memory.confidence > 0.6:
                memory.status = "VALIDATED"
                
        # Record evidence
        evidence = MemoryEvidence(
            memory_id=memory.id,
            conversation_id=conversation_id,
            evidence_type=evidence_type,
            weight=weight
        )
        self.session.add(evidence)
        await self.session.commit()
        await self.session.refresh(memory)
        return memory

    async def get_active_memories(self, user_id: uuid.UUID) -> List[Memory]:
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.status.in_(["ACTIVE", "VALIDATED"])
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
        
    async def delete_memory(self, user_id: uuid.UUID, memory_id: uuid.UUID) -> bool:
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.id == memory_id
        )
        result = await self.session.execute(stmt)
        memory = result.scalars().first()
        
        if memory:
            memory.status = "DELETED"
            await self.session.commit()
            return True
        return False
