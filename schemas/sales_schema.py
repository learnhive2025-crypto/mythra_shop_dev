from pydantic import BaseModel
from typing import List

class SalesItemSchema(BaseModel):
    barcode: str        # 👈 barcode scan value
    qty: int            # 👈 staff enters qty

class SalesCreateSchema(BaseModel):
    bill_no: str
    items: List[SalesItemSchema]
    payment_mode: str
