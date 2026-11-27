import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.history import QueryHistory
from app.schemas.dataset import HistoryItemResponse, HistoryDetailResponse

router = APIRouter(prefix="/api/history", tags=["history"])


def _item_to_response(h: QueryHistory) -> HistoryItemResponse:
    return HistoryItemResponse(
        id=h.id, dataset_id=h.dataset_id, query_text=h.query_text,
        agents_used=json.loads(h.agents_used_json or "[]"), created_at=h.created_at,
    )


@router.get("", response_model=List[HistoryItemResponse])
def list_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(QueryHistory).filter(QueryHistory.owner_id == current_user.id) \
        .order_by(QueryHistory.created_at.desc()).all()
    return [_item_to_response(h) for h in items]


@router.get("/{history_id}", response_model=HistoryDetailResponse)
def get_history_item(history_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    h = db.query(QueryHistory).filter(
        QueryHistory.id == history_id, QueryHistory.owner_id == current_user.id
    ).first()
    if not h:
        raise HTTPException(status_code=404, detail="History item not found")
    base = _item_to_response(h)
    return HistoryDetailResponse(**base.dict(), result=json.loads(h.result_json or "{}"))
