from datetime import datetime

def expense_model(
    date: str,
    category: str,
    amount: float,
    description: str = None
):
    """
    Model for general daily expenses.
    """
    return {
        "date": date,           # ISO format string (e.g., YYYY-MM-DD)
        "category": category,
        "amount": amount,
        "description": description,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }
