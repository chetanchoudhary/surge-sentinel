from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, HttpUrl


class DynamicField(BaseModel):
    type: str
    values: Optional[List[Any]] = None


class TestConfigBase(BaseModel):
    name: str
    url: str
    method: str
    headers: Optional[Dict[str, str]] = None
    payload_template: Optional[Dict[str, Any]] = None
    dynamic_fields: Optional[Dict[str, DynamicField]] = None
    num_requests: int
    concurrency: int
    use_proxies: bool = False
    proxy_rotation_strategy: str = "round_robin"


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


class TestResultBase(BaseModel):
    config_id: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: Optional[float] = None
    status_code_distribution: Optional[Dict[str, int]] = None
    error_messages: Optional[List[str]] = None
    proxy_performance: Optional[Dict[str, float]] = None


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
    test_id: str


class TestResultResponse(BaseModel):
    message: str


class TestConfigResponse(BaseModel):
    test_configs: List[TestConfig]


class DeleteTestConfigResponse(BaseModel):
    message: str


class ProxyRequest(BaseModel):
    url: HttpUrl


class ProxyResponse(BaseModel):
    message: str
