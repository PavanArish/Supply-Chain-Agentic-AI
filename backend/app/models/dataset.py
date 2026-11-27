from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    stored_path = Column(String(1000), nullable=False)
    file_type = Column(String(20), nullable=False)  # csv, xlsx, xls
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    column_roles_json = Column(Text)  # JSON string: detected column -> role mapping
    schema_json = Column(Text)  # JSON string: column -> dtype
    created_at = Column(DateTime(timezone=True), server_default=func.now())
