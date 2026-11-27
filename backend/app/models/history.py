from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    agents_used_json = Column(Text)  # JSON list of agent names
    result_json = Column(Text)  # JSON: full structured result (insights, charts, recs, risks)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
