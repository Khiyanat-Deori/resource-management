from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional

from app.db.session import SessionLocal
from app.models.history import TimeHistory
from app.schemas.history import TimeHistoryResponse
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/time", tags=["Time"])

@router.get("/history", response_model=List[TimeHistoryResponse])
def get_history(
    start_date: Optional[date] = Query(None),
end_date: Optional[date] = Query(None),
    db: Session = Depends(SessionLocal),
    current_user: User = Depends(get_current_user),
):
    query = db.query(TimeHistory).filter(
        TimeHistory.user_id == current_user.id
    )

    if from_date:
        query = query.filter(TimeHistory.clock_in >= from_date)

    if to_date:
        query = query.filter(TimeHistory.clock_in <= to_date)

    return query.order_by(TimeHistory.clock_in.desc()).all()

@router.get("/history/{day}", response_model=List[TimeHistoryResponse])
def get_history_for_day(
    day: date,
    db: Session = Depends(SessionLocal),
    current_user: User = Depends(get_current_user),
):
    start = datetime.combine(day, datetime.min.time())
    end = datetime.combine(day, datetime.max.time())

    return (
        db.query(TimeHistory)
        .filter(
            TimeHistory.user_id == current_user.id,
            TimeHistory.clock_in >= start,
            TimeHistory.clock_in <= end,
        )
        .order_by(TimeHistory.clock_in.asc())
        .all()
    )
