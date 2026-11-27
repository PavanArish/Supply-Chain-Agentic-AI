from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class DatasetResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    row_count: int
    column_count: int
    column_roles: Dict[str, str]
    column_schema: Dict[str, str]
    created_at: datetime

    class Config:
        from_attributes = True


class DataPreviewResponse(BaseModel):
    columns: List[str]
    dtypes: Dict[str, str]
    missing: Dict[str, int]
    sample_rows: List[Dict[str, Any]]
    row_count: int


class QueryRequest(BaseModel):
    dataset_id: int
    query: str


class QueryResultResponse(BaseModel):
    history_id: int
    agents_used: List[str]
    insights: List[str]
    charts: List[Dict[str, Any]]
    recommendations: List[str]
    risk_alerts: List[str]


class HistoryItemResponse(BaseModel):
    id: int
    dataset_id: int
    query_text: str
    agents_used: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryDetailResponse(HistoryItemResponse):
    result: Dict[str, Any]
