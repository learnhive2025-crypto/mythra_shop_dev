from datetime import datetime

def category_model(name: str, is_active: bool = True):
    return {
        "name": name,
        "is_active": is_active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
