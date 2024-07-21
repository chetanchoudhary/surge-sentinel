from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from src.db.base import Base


class TestConfig(Base):
    __tablename__ = "test_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    method = Column(String)
    headers = Column(JSON)
    payload_template = Column(JSON)
    dynamic_fields = Column(JSON)
    num_requests = Column(Integer)
    concurrency = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, index=True)
    total_requests = Column(Integer)
    successful_requests = Column(Integer)
    failed_requests = Column(Integer)
    average_response_time = Column(Float)
    status_code_distribution = Column(JSON)
    error_messages = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
