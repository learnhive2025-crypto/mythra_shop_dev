from pydantic import BaseModel
from typing import Optional
from datetime import date

class ExpenseCreateSchema(BaseModel):
    date: Optional[str] = None # Will default to today if not provided
    category: str
    amount: float
    description: Optional[str] = None

class ExpenseUpdateSchema(BaseModel):
    date: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
