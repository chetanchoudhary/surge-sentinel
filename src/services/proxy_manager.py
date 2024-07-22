from datetime import datetime, timedelta
from typing import Dict, List

import httpx
from pydantic import BaseModel, HttpUrl


class Proxy(BaseModel):
    url: HttpUrl
    last_used: datetime = datetime.min
    fail_count: int = 0
    success_count: int = 0
    last_status_code: int = 0
    average_response_time: float = 0


class ProxyManager:
    def __init__(self):
        self.proxies: Dict[str, Proxy] = {}
        self.rate_limit_threshold = (
            3  # Number of 429 responses before considering rate limited
        )

    async def add_proxy(self, url: HttpUrl):
        if url not in self.proxies:
            self.proxies[url] = Proxy(url=url)
        await self.health_check(url)

    async def remove_proxy(self, url: HttpUrl):
        self.proxies.pop(url, None)

    async def health_check(self, url: HttpUrl):
        async with httpx.AsyncClient() as client:
            try:
                start_time = datetime.now()
                response = await client.get(
                    "http://example.com", proxies={"all://": str(url)}
                )
                elapsed = (datetime.now() - start_time).total_seconds()
                self.proxies[url].last_status_code = response.status_code
                self.proxies[url].average_response_time = elapsed
                self.proxies[url].success_count += 1
            except Exception:
                self.proxies[url].fail_count += 1

    async def get_proxy(self, strategy: str = "round_robin") -> HttpUrl:
        if not self.proxies:
            raise ValueError("No proxies available")

        if strategy == "round_robin":
            return self._get_round_robin_proxy()
        elif strategy == "least_used":
            return self._get_least_used_proxy()
        else:
            raise ValueError(f"Unknown proxy rotation strategy: {strategy}")

    def _get_round_robin_proxy(self) -> HttpUrl:
        sorted_proxies = sorted(self.proxies.values(), key=lambda p: p.last_used)
        proxy = sorted_proxies[0]
        proxy.last_used = datetime.now()
        return proxy.url

    def _get_least_used_proxy(self) -> HttpUrl:
        sorted_proxies = sorted(self.proxies.values(), key=lambda p: p.success_count)
        return sorted_proxies[0].url

    def update_proxy_status(self, url: HttpUrl, status_code: int, response_time: float):
        if url in self.proxies:
            proxy = self.proxies[url]
            proxy.last_status_code = status_code
            proxy.average_response_time = (
                proxy.average_response_time * proxy.success_count + response_time
            ) / (proxy.success_count + 1)
            if status_code == 429:
                proxy.fail_count += 1
            else:
                proxy.success_count += 1

    def is_rate_limited(self, url: HttpUrl) -> bool:
        if url in self.proxies:
            return self.proxies[url].fail_count >= self.rate_limit_threshold
        return False


proxy_manager = ProxyManager()
