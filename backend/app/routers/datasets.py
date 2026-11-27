from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetResponse, DataPreviewResponse
from app.services.dataset_service import save_and_process_upload, dataset_to_response
from app.services.df_cache import get_or_load

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetResponse)
def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = save_and_process_upload(db, current_user.id, file)
    return dataset_to_response(dataset)


@router.get("", response_model=List[DatasetResponse])
def list_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    datasets = db.query(Dataset).filter(Dataset.owner_id == current_user.id).order_by(Dataset.created_at.desc()).all()
    return [dataset_to_response(d) for d in datasets]


@router.get("/{dataset_id}/preview", response_model=DataPreviewResponse)
def preview_dataset(dataset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = get_or_load(dataset.id, dataset.stored_path, dataset.file_type)
    sample = df.head(20).astype(str).to_dict(orient="records")
    return DataPreviewResponse(
        columns=list(df.columns),
        dtypes={c: str(df[c].dtype) for c in df.columns},
        missing={c: int(df[c].isna().sum()) for c in df.columns},
        sample_rows=sample,
        row_count=len(df),
    )
