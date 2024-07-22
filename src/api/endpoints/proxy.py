from fastapi import APIRouter, HTTPException

from src.schemas.load_test import ProxyRequest, ProxyResponse
from src.services.proxy_manager import proxy_manager

router = APIRouter()


@router.post("/proxy", response_model=ProxyResponse)
async def add_proxy(proxy: ProxyRequest):
    await proxy_manager.add_proxy(proxy.url)
    return ProxyResponse(message=f"Proxy {proxy.url} added successfully")


@router.delete("/proxy", response_model=ProxyResponse)
async def remove_proxy(proxy: ProxyRequest):
    await proxy_manager.remove_proxy(proxy.url)
    return ProxyResponse(message=f"Proxy {proxy.url} removed successfully")


@router.get("/proxies")
async def get_proxies():
    return list(proxy_manager.proxies.keys())


@router.post("/proxy/health_check", response_model=ProxyResponse)
async def health_check_proxy(proxy: ProxyRequest):
    if proxy.url not in proxy_manager.proxies:
        raise HTTPException(status_code=404, detail="Proxy not found")
    await proxy_manager.health_check(proxy.url)
    return ProxyResponse(message=f"Health check completed for proxy {proxy.url}")
