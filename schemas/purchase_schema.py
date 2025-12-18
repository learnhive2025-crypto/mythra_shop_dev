from pydantic import BaseModel
from typing import List

# ---------------- PURCHASE ITEM ----------------
class PurchaseItemSchema(BaseModel):
    product_id: str
    qty: int
    price: float

# ---------------- CREATE PURCHASE ----------------
class PurchaseCreateSchema(BaseModel):
    invoice_no: str
    supplier_name: str
    items: List[PurchaseItemSchema]

# ---------------- UPDATE PURCHASE ----------------
class PurchaseUpdateSchema(BaseModel):
    invoice_no: str
    supplier_name: str
    items: List[PurchaseItemSchema]
