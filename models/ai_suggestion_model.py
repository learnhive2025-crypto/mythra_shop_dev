from datetime import datetime

def ai_suggestion_model(
    suggestion_type: str,
    title: str,
    description: str,
    priority: str = "medium",
    data_insights: dict = None
):
    """
    Model for AI-generated business suggestions.
    
    Args:
        suggestion_type: Type of suggestion (sales, inventory, expense, marketing, etc.)
        title: Short title of the suggestion
        description: Detailed description and actionable steps
        priority: Priority level (low, medium, high, critical)
        data_insights: Supporting data that led to this suggestion
    """
    return {
        "suggestion_type": suggestion_type,
        "title": title,
        "description": description,
        "priority": priority,
        "data_insights": data_insights or {},
        "status": "new",  # new, read, implemented, dismissed
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "is_active": True
    }
