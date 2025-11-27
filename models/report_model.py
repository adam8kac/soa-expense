from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_serializer

from models.expense_model import ExpenseResponse
from models.item_model import Item


class Report(BaseModel):
    date_from: Optional[date]
    date_to: Optional[date]
    expenses: list[ExpenseResponse]
    most_expensive_items: list[Item]
    total_price: float
    created_at: datetime

    @field_serializer("created_at", mode="plain", when_used="json")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y/%m/%d %H:%M:%S")
