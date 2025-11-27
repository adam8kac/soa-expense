from pydantic import BaseModel, Field
import uuid


class Item(BaseModel):
    item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_name: str
    item_price: float
    item_quantity: int
