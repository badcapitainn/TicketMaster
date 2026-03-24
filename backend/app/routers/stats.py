from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import require_admin
from app.crud.ticket import get_stats

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get("", dependencies=[Depends(require_admin)])
def statistics(db: Session = Depends(get_db)):
    """
    Get ticket statistics broken down by status and priority.
    **Admin only.**
    """
    return get_stats(db)
