from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseDTO(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: T | None = None
    error: Any | None = None
