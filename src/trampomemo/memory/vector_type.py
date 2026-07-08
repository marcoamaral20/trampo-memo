import json
from typing import Any

from sqlalchemy import JSON
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator, UserDefinedType


class PostgreSQLVector(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw: Any) -> str:
        return "vector"


class Vector(TypeDecorator):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQLVector())
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: list[float] | None, dialect: Dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return "[" + ",".join(str(item) for item in value) + "]"
        return value

    def process_result_value(self, value: Any, dialect: Dialect) -> list[float] | None:
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [float(item) for item in json.loads(value)]
        return value
