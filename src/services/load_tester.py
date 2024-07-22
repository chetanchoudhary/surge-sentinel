import asyncio
import time
from collections import Counter, defaultdict

import httpx

from src.models.load_test import TestConfig
from src.schemas.load_test import TestResult  # Import Pydantic TestResult
from src.services.proxy_manager import proxy_manager
from src.utils.dynamic_field_generator import generate_dynamic_value


class LoadTester:
    def __init__(self, config: TestConfig, test_id: str):  # Added test_id parameter
        self.config = config
        self.test_id = test_id  # Store test_id
        self.results = defaultdict(list)
        self.proxy_performance = defaultdict(list)

    async def get_proxy(self):
        if not self.config.use_proxies:
            return None
        return await proxy_manager.get_proxy(self.config.proxy_rotation_strategy)

    def generate_dynamic_payload(self):
        if not self.config.payload_template or not self.config.dynamic_fields:
            return self.config.payload_template

        payload = self.config.payload_template.copy()
        for field, field_config in self.config.dynamic_fields.items():
            payload[field] = generate_dynamic_value(field_config)
        return payload

    async def make_request(self, client):
        start_time = time.time()
        proxy = await self.get_proxy()
        try:
            payload = self.generate_dynamic_payload()
            response = await client.request(
                method=self.config.method,
                url=self.config.url,
                headers=self.config.headers,
                json=payload,
                # proxies={"all://": str(proxy)} if proxy else None
            )
            elapsed = time.time() - start_time
            self.results["response_times"].append(elapsed)
            self.results["status_codes"].append(response.status_code)
            if proxy:
                self.proxy_performance[str(proxy)].append(elapsed)
                proxy_manager.update_proxy_status(proxy, response.status_code, elapsed)

            if response.status_code == 429:  # Rate limit hit
                await self.handle_rate_limit(proxy)

            return response
        except Exception as e:
            self.results["errors"].append(str(e))
            if proxy:
                self.proxy_performance[str(proxy)].append(None)  # Indicate failure
                proxy_manager.update_proxy_status(proxy, 0, 0)  # Indicate failure
            raise

    async def handle_rate_limit(self, proxy):
        if proxy:
            print(f"Rate limit hit for proxy {proxy}. Switching proxy.")
            # The next request will automatically use a different proxy
        else:
            print("Rate limit hit. Implementing backoff strategy.")
            await asyncio.sleep(5)  # Simple backoff strategy

    async def run(self):
        async with httpx.AsyncClient() as client:
            tasks = [self.make_request(client) for _ in range(self.config.num_requests)]
            semaphore = asyncio.Semaphore(self.config.concurrency)

            async def bounded_request(task):
                async with semaphore:
                    return await task

            await asyncio.gather(*[bounded_request(task) for task in tasks])

    def generate_report(self) -> TestResult:
        import datetime

        return TestResult(
            id=self.config.id,
            created_at=datetime.datetime.now(),
            test_id=self.test_id,
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
            proxy_performance={
                proxy: sum(times) / len(times)
                for proxy, times in self.proxy_performance.items()
                if any(t is not None for t in times)
            },
        )
