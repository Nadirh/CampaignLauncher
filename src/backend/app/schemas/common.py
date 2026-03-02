from pydantic import BaseModel


class ErrorDetail(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
