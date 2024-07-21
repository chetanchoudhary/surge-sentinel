import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, List, Optional

from pydantic import BaseModel


class DynamicField(BaseModel):
    type: str
    values: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    format: Optional[str] = None


def generate_dynamic_value(field: DynamicField) -> Any:
    if field.values:
        return random.choice(field.values)

    if field.type == "string":
        return generate_string(field)
    elif field.type == "integer":
        return generate_integer(field)
    elif field.type == "float":
        return generate_float(field)
    elif field.type == "boolean":
        return random.choice([True, False])
    elif field.type == "date":
        return generate_date(field)
    elif field.type == "email":
        return generate_email()
    else:
        raise ValueError(f"Unsupported field type: {field.type}")


def generate_string(field: DynamicField) -> str:
    if field.format == "uuid":
        return str(uuid.uuid4())
    elif field.format == "name":
        return f"{random.choice(['John', 'Jane', 'Alice', 'Bob', 'Charlie'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
    else:
        length = random.randint(5, 15)
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_integer(field: DynamicField) -> int:
    min_value = field.min_value if field.min_value is not None else 0
    max_value = field.max_value if field.max_value is not None else 1000
    return random.randint(int(min_value), int(max_value))


def generate_float(field: DynamicField) -> float:
    min_value = field.min_value if field.min_value is not None else 0.0
    max_value = field.max_value if field.max_value is not None else 1000.0
    return random.uniform(float(min_value), float(max_value))


def generate_date(field: DynamicField) -> str:
    if field.format == "iso":
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now() + timedelta(days=365)
        random_date = start_date + timedelta(days=random.randint(0, 730))
        return random_date.isoformat()
    else:
        return datetime.now().strftime("%Y-%m-%d")


def generate_email() -> str:
    username_length = random.randint(5, 10)
    username = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=username_length)
    )
    domain = random.choice(["gmail.com", "yahoo.com", "hotmail.com", "example.com"])
    return f"{username}@{domain}"
