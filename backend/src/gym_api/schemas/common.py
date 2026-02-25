from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = []


class Meta(BaseModel):
    request_id: str = ""


class ErrorResponse(BaseModel):
    error: ErrorBody
    meta: Meta = Meta()


class PaginationMeta(BaseModel):
    next_cursor: str | None = None
    has_more: bool = False
    limit: int = 20


class PaginatedResponse(BaseModel):
    data: list = []
    pagination: PaginationMeta = PaginationMeta()
    meta: Meta = Meta()


class CursorParams(BaseModel):
    cursor: str | None = Field(None, description="Opaque cursor for next page")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
