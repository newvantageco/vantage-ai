from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Dict, Any
from uuid import uuid4


@dataclass
class PostResult:
    id: Optional[str]
    url: Optional[str]
    external_refs: Optional[Dict[str, str]] = None  # provider -> ref_id mapping


class Publisher:
    can_schedule: bool = True

    async def publish(
        self,
        *,
        caption: str,
        media_paths: Sequence[str],
        first_comment: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PostResult:
        raise NotImplementedError
    
    def store_external_reference(
        self,
        schedule_id: str,
        provider: str,
        ref_id: str,
        ref_url: Optional[str] = None,
        db_session = None
    ) -> Optional[str]:
        """
        Store external reference for a schedule.
        
        Args:
            schedule_id: Schedule ID
            provider: Platform provider name
            ref_id: Platform-specific post ID
            ref_url: Platform-specific post URL
            db_session: Database session (optional)
            
        Returns:
            External reference ID if stored successfully
        """
        if not db_session:
            return None
        
        try:
            from app.models.external_refs import ScheduleExternal
            
            external_ref = ScheduleExternal(
                id=str(uuid4()),
                schedule_id=schedule_id,
                ref_id=ref_id,
                ref_url=ref_url,
                provider=provider
            )
            
            db_session.add(external_ref)
            return external_ref.id
            
        except Exception as e:
            # Log error but don't fail the publish operation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to store external reference: {e}")
            return None


