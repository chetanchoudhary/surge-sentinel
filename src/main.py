import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints import load_test, proxy, test_config
from src.core.config import settings
from src.db.base import Base
from src.db.session import engine

app = FastAPI(title=settings.APP_NAME)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(load_test.router, prefix="/api/v1")
app.include_router(test_config.router, prefix="/api/v1")
app.include_router(proxy.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()


def start():
    """Launched with `poetry run start` at root level"""
    live_reload = True
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=5000,
        reload=live_reload,
        workers=1,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000, reload=settings.DEBUG)
