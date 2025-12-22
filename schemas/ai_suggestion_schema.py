from pydantic import BaseModel
from typing import Optional, Dict

class AISuggestionUpdateSchema(BaseModel):
    status: Optional[str] = None  # new, read, implemented, dismissed
    is_active: Optional[bool] = None
