from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.session import get_db
from src.models.load_test import TestConfig as DBTestConfig
from src.schemas.load_test import (
    DeleteTestConfigResponse,
    TestConfig,
    TestConfigCreate,
    TestConfigResponse,
    TestConfigUpdate,
)

router = APIRouter()


@router.post("/test_config", response_model=TestConfig)
async def create_test_config(
    config: TestConfigCreate, db: AsyncSession = Depends(get_db)
):
    db_config = DBTestConfig(**config.dict())
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return TestConfig.from_orm(db_config)


@router.get("/test_configs", response_model=TestConfigResponse)
async def get_test_configs(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(DBTestConfig).offset(skip).limit(limit))
    configs = result.scalars().all()
    return TestConfigResponse(
        test_configs=[TestConfig.from_orm(config) for config in configs]
    )


@router.get("/test_config/{config_id}", response_model=TestConfig)
async def get_test_config(config_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBTestConfig).filter(DBTestConfig.id == config_id))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="Test configuration not found")
    return TestConfig.from_orm(config)


@router.put("/test_config/{config_id}", response_model=TestConfig)
async def update_test_config(
    config_id: int, updated_config: TestConfigUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(DBTestConfig).filter(DBTestConfig.id == config_id))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="Test configuration not found")

    update_data = updated_config.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    await db.commit()
    await db.refresh(config)
    return TestConfig.from_orm(config)


@router.delete("/test_config/{config_id}", response_model=DeleteTestConfigResponse)
async def delete_test_config(config_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBTestConfig).filter(DBTestConfig.id == config_id))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="Test configuration not found")

    await db.delete(config)
    await db.commit()
    return DeleteTestConfigResponse(message="Test configuration deleted successfully")
