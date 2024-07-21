import asyncio
import random
import string
import time
import uuid
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Union

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class DynamicField(BaseModel):
    type: str
    values: Optional[List[Any]] = None


class TestConfig(BaseModel):
    name: str
    url: str
    method: str
    headers: Optional[Dict[str, str]] = None
    payload_template: Optional[Dict[str, Any]] = None
    dynamic_fields: Optional[Dict[str, DynamicField]] = None
    num_requests: int
    concurrency: int


class TestResult(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    status_code_distribution: Dict[str, int]
    error_messages: List[str]


test_configs = {}


class LoadTester:
    def __init__(self, config: TestConfig):
        self.config = config
        self.results = defaultdict(list)

    def generate_dynamic_value(self, field: DynamicField) -> Any:
        if field.values:
            return random.choice(field.values)
        elif field.type == "email":
            return f"user{random.randint(1, 1000000)}@example.com"
        elif field.type == "string":
            return "".join(random.choices(string.ascii_letters + string.digits, k=10))
        elif field.type == "integer":
            return random.randint(1, 1000000)
        elif field.type == "float":
            return round(random.uniform(0, 1000), 2)
        else:
            return f"random_{field.type}_{random.randint(1, 1000000)}"

    def generate_dynamic_payload(self):
        if not self.config.payload_template or not self.config.dynamic_fields:
            return self.config.payload_template

        payload = self.config.payload_template.copy()
        for field, field_config in self.config.dynamic_fields.items():
            payload[field] = self.generate_dynamic_value(field_config)
        return payload

    async def make_request(self, client):
        start_time = time.time()
        try:
            payload = self.generate_dynamic_payload()
            response = await client.request(
                method=self.config.method,
                url=self.config.url,
                headers=self.config.headers,
                json=payload,
            )
            elapsed = time.time() - start_time
            self.results["response_times"].append(elapsed)
            self.results["status_codes"].append(response.status_code)
        except Exception as e:
            self.results["errors"].append(str(e))

    async def run(self):
        async with httpx.AsyncClient() as client:
            tasks = [self.make_request(client) for _ in range(self.config.num_requests)]
            await asyncio.gather(*tasks)

    def generate_report(self) -> TestResult:
        return TestResult(
            total_requests=self.config.num_requests,
            successful_requests=len(self.results["response_times"]),
            failed_requests=len(self.results["errors"]),
            average_response_time=sum(self.results["response_times"])
            / len(self.results["response_times"])
            if self.results["response_times"]
            else 0,
            status_code_distribution={
                str(k): v
                for k, v in dict(Counter(self.results["status_codes"])).items()
            },
            error_messages=self.results["errors"],
        )


@app.post("/run_test")
async def run_test(config: TestConfig, background_tasks: BackgroundTasks):
    tester = LoadTester(config)
    background_tasks.add_task(tester.run)
    return {"message": "Test started", "test_id": id(tester)}


@app.get("/test_result/{test_id}")
async def get_test_result(test_id: int):
    tester = asyncio.current_task()
    if tester and id(tester) == test_id:
        return tester.generate_report()
    return {"message": "Test not found or still running"}


@app.post("/save_test_config")
async def save_test_config(config: TestConfig):
    config_id = str(uuid.uuid4())
    test_configs[config_id] = config
    return {"message": "Test configuration saved", "config_id": config_id}


@app.get("/test_configs")
async def get_test_configs():
    return list(test_configs.values())


@app.get("/test_config/{config_id}")
async def get_test_config(config_id: str):
    if config_id not in test_configs:
        raise HTTPException(status_code=404, detail="Test configuration not found")
    return test_configs[config_id]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
