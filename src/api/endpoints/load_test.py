import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.session import get_db
from src.models.load_test import TestConfig as DBTestConfig
from src.models.load_test import TestResult as DBTestResult
from src.schemas.load_test import (
    RunTestRequest,
    RunTestResponse,
    TestResult,
    TestResultResponse,
)
from src.services.load_tester import LoadTester

router = APIRouter()


@router.post("/run_test", response_model=RunTestResponse)
async def run_test(
    request: RunTestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DBTestConfig).filter(DBTestConfig.id == request.config_id)
    )
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="Test configuration not found")

    tester = LoadTester(config)
    background_tasks.add_task(tester.run)
    return RunTestResponse(message="Test started", test_id=id(tester))


@router.get("/test_result/{test_id}", response_model=TestResult)
async def get_test_result(test_id: int, db: AsyncSession = Depends(get_db)):
    tester = asyncio.current_task()
    if tester and id(tester) == test_id:
        result = tester.generate_report()
        db_result = DBTestResult(**result.dict())
        db.add(db_result)
        await db.commit()
        return TestResult.from_orm(db_result)
    raise HTTPException(status_code=404, detail="Test not found or still running")
