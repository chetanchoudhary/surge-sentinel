import asyncio
import time
from collections import Counter, defaultdict

import httpx

from src.models.load_test import TestConfig, TestResult
from src.utils.dynamic_field_generator import generate_dynamic_value


class LoadTester:
    def __init__(self, config: TestConfig):
        self.config = config
        self.results = defaultdict(list)

    def generate_dynamic_payload(self):
        if not self.config.payload_template or not self.config.dynamic_fields:
            return self.config.payload_template

        payload = self.config.payload_template.copy()
        for field, field_config in self.config.dynamic_fields.items():
            payload[field] = generate_dynamic_value(field_config)
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
            config_id=self.config.id,
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
