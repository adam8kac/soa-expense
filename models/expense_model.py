from datetime import datetime
from pydantic import BaseModel, field_serializer

from models.item_model import Item


class ExpenseResponse(BaseModel):
    description: str
    items: list[Item]
    total_price: float
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at", mode="plain", when_used="json")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y/%m/%d %H:%M:%S")


class ExpenseRequest(BaseModel):
    description: str
    items: list[Item]
