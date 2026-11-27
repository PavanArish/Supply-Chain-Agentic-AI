import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.models.history import QueryHistory
from app.schemas.dataset import QueryRequest, QueryResultResponse
from app.services.df_cache import get_or_load
from app.orchestrator.agent_manager import run_query

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("", response_model=QueryResultResponse)
def submit_query(payload: QueryRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = db.query(Dataset).filter(
        Dataset.id == payload.dataset_id, Dataset.owner_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = get_or_load(dataset.id, dataset.stored_path, dataset.file_type)
    roles = json.loads(dataset.column_roles_json or "{}")

    result = run_query(df, roles, payload.query)

    history = QueryHistory(
        owner_id=current_user.id,
        dataset_id=dataset.id,
        query_text=payload.query,
        agents_used_json=json.dumps(result["agents_used"]),
        result_json=json.dumps({
            "insights": result["insights"],
            "charts": result["charts"],
            "recommendations": result["recommendations"],
            "risk_alerts": result["risk_alerts"],
        }, default=str),
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    return QueryResultResponse(
        history_id=history.id,
        agents_used=result["agents_used"],
        insights=result["insights"],
        charts=result["charts"],
        recommendations=result["recommendations"],
        risk_alerts=result["risk_alerts"],
    )
