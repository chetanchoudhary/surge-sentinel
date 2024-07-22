from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.session import get_db
from src.models.load_test import TestConfig as DBTestConfig
from src.models.load_test import TestResult as DBTestResult
from src.schemas.load_test import RunTestRequest, RunTestResponse, TestResult
from src.services.load_tester import LoadTester
from src.services.test_result_manager import test_result_manager

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

    test_id = test_result_manager.create_test()
    tester = LoadTester(config, test_id)  # Pass test_id to LoadTester
    # background_tasks.add_task(run_test_task, tester, test_id)
    await run_test_task(tester, test_id)
    return RunTestResponse(message="Test started", test_id=test_id)


async def run_test_task(tester: LoadTester, test_id: str):
    await tester.run()
    result = tester.generate_report()
    test_result_manager.set_test_result(test_id, result)


@router.get("/test_result/{test_id}", response_model=TestResult)
async def get_test_result(test_id: str, db: AsyncSession = Depends(get_db)):
    result = test_result_manager.get_test_result(test_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Test not found or still running")

    db_result = await db.execute(
        select(DBTestResult).filter(DBTestResult.test_id == test_id)
    )
    existing_result = db_result.scalars().first()

    if existing_result is None:
        print(result)
        db_result = DBTestResult(**result.model_dump())
        db.add(db_result)
        await db.commit()
        await db.refresh(db_result)
    else:
        db_result = existing_result

    return TestResult.from_orm(db_result)
