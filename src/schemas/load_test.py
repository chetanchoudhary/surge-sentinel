from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, HttpUrl


# TestConfig schemas
class DynamicField(BaseModel):
    type: str
    values: Optional[List[Any]] = None


class TestConfigBase(BaseModel):
    name: str
    url: HttpUrl
    method: str
    headers: Optional[Dict[str, str]] = None
    payload_template: Optional[Dict[str, Any]] = None
    dynamic_fields: Optional[Dict[str, DynamicField]] = None
    num_requests: int
    concurrency: int


class TestConfigCreate(TestConfigBase):
    pass


class TestConfigUpdate(TestConfigBase):
    pass


class TestConfig(TestConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# TestResult schemas
class TestResultBase(BaseModel):
    config_id: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    status_code_distribution: Dict[str, int]
    error_messages: List[str]


class TestResultCreate(TestResultBase):
    pass


class TestResult(TestResultBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# API specific request/response models
class RunTestRequest(BaseModel):
    config_id: int


class RunTestResponse(BaseModel):
    message: str
    test_id: int


class TestResultResponse(BaseModel):
    message: str


class TestConfigResponse(BaseModel):
    test_configs: List[TestConfig]


class DeleteTestConfigResponse(BaseModel):
    message: str
