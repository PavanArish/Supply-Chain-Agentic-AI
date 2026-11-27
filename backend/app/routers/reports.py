import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.history import QueryHistory
from app.services import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])

MEDIA_TYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
}


@router.get("/{history_id}/{fmt}")
def download_report(history_id: int, fmt: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if fmt not in MEDIA_TYPES:
        raise HTTPException(status_code=400, detail="Format must be one of: csv, xlsx, pdf")

    h = db.query(QueryHistory).filter(
        QueryHistory.id == history_id, QueryHistory.owner_id == current_user.id
    ).first()
    if not h:
        raise HTTPException(status_code=404, detail="History item not found")

    result = json.loads(h.result_json or "{}")

    if fmt == "csv":
        path = report_service.generate_csv(result)
    elif fmt == "xlsx":
        path = report_service.generate_excel(result)
    else:
        path = report_service.generate_pdf(result, query_text=h.query_text)

    filename = f"supply_chain_report_{history_id}.{fmt}"
    return FileResponse(path, media_type=MEDIA_TYPES[fmt], filename=filename)
