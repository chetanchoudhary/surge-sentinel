import uuid
from typing import Dict, Optional

from src.schemas.load_test import TestResult


class TestResultManager:
    def __init__(self):
        self.results: Dict[str, Optional[TestResult]] = {}

    def create_test(self) -> str:
        test_id = str(uuid.uuid4())
        self.results[test_id] = None
        return test_id

    def set_test_result(self, test_id: str, result: TestResult):
        if test_id in self.results:
            self.results[test_id] = result

    def get_test_result(self, test_id: str) -> Optional[TestResult]:
        return self.results.get(test_id)


test_result_manager = TestResultManager()
