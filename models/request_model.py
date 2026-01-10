from datetime import datetime
from pydantic import BaseModel, field_serializer, Field


class CallRequest(BaseModel):
    klicanaStoritev: str = Field(..., alias="klicanaStoritev")

    class Config:
        populate_by_name = True


class StatisticsResponse(BaseModel):
    called_service: str
    call_count: int
