import json
import os
import uuid
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.models.dataset import Dataset
from app.services.data_cleaning import clean_dataframe, profile_dataframe
from app.services.column_mapper import detect_column_roles, coerce_dates
from app.services.df_cache import set_df

ALLOWED_EXT = {"csv", "xlsx", "xls"}


def _read_raw(path: str, ext: str) -> pd.DataFrame:
    if ext == "csv":
        return pd.read_csv(path)
    return pd.read_excel(path)


def save_and_process_upload(db: Session, owner_id: int, file: UploadFile) -> Dataset:
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Only .csv, .xlsx, .xls files are supported")

    safe_name = f"{uuid.uuid4().hex}.{ext}"
    stored_path = os.path.join(settings.upload_dir, safe_name)
    with open(stored_path, "wb") as f:
        f.write(file.file.read())

    try:
        df = _read_raw(stored_path, ext)
    except Exception as e:
        os.remove(stored_path)
        raise HTTPException(status_code=400, detail=f"Could not parse file: {e}")

    # Input Processor: validation & cleaning, profiling, schema/role extraction
    df, _notes = clean_dataframe(df)
    roles = detect_column_roles(df)
    df = coerce_dates(df, roles)
    profile = profile_dataframe(df)

    dataset = Dataset(
        owner_id=owner_id,
        filename=file.filename,
        stored_path=stored_path,
        file_type=ext,
        row_count=profile["row_count"],
        column_count=profile["column_count"],
        column_roles_json=json.dumps(roles),
        schema_json=json.dumps(profile["dtypes"]),
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    set_df(dataset.id, df)
    return dataset


def dataset_to_response(dataset: Dataset) -> dict:
    return {
        "id": dataset.id,
        "filename": dataset.filename,
        "file_type": dataset.file_type,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "column_roles": json.loads(dataset.column_roles_json or "{}"),
        "column_schema": json.loads(dataset.schema_json or "{}"),
        "created_at": dataset.created_at,
    }
