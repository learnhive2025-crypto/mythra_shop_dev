from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime, timedelta
from database import db
from schemas.ai_suggestion_schema import AISuggestionUpdateSchema
from models.ai_suggestion_model import ai_suggestion_model
from utils.security import admin_or_super_admin
from utils.ai_service import AIBusinessAnalyzer

ai_suggestions_collection = db["ai_suggestions"]

router = APIRouter(
    prefix="/ai-suggestions",
    tags=["AI Suggestions"]
)

@router.post("/generate")
def generate_daily_suggestions(user=Depends(admin_or_super_admin)):
    """
    Generate AI-powered business suggestions based on current data.
    This can be called daily to get fresh insights.
    """
    try:
        # Check if suggestions were already generated today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        existing_today = ai_suggestions_collection.count_documents({
            "created_at": {"$gte": today_start},
            "is_active": True
        })
        
        # Generate new suggestions
        suggestions = AIBusinessAnalyzer.generate_suggestions()
        
        # Save to database
        saved_count = 0
        for suggestion in suggestions:
            ai_suggestions_collection.insert_one(
                ai_suggestion_model(
                    suggestion_type=suggestion["type"],
                    title=suggestion["title"],
                    description=suggestion["description"],
                    priority=suggestion["priority"],
                    data_insights=suggestion["data_insights"]
                )
            )
            saved_count += 1
        
        return {
            "message": f"Generated {saved_count} new suggestions",
            "suggestions": suggestions,
            "existing_today": existing_today
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate suggestions: {str(e)}")

@router.get("/today")
def get_today_suggestions(user=Depends(admin_or_super_admin)):
    """Get today's AI suggestions"""
    try:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        suggestions = list(ai_suggestions_collection.find({
            "created_at": {"$gte": today_start},
            "is_active": True
        }).sort("priority", -1))
        
        # Convert priority to numeric for sorting
        priority_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        suggestions.sort(key=lambda x: priority_map.get(x.get("priority", "low"), 1), reverse=True)
        
        for suggestion in suggestions:
            suggestion["_id"] = str(suggestion["_id"])
        
        return {
            "count": len(suggestions),
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch suggestions: {str(e)}")

@router.get("/history")
def get_suggestion_history(
    days: int = 7,
    user=Depends(admin_or_super_admin)
):
    """Get suggestion history for the last N days"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        suggestions = list(ai_suggestions_collection.find({
            "created_at": {"$gte": start_date},
            "is_active": True
        }).sort("created_at", -1))
        
        for suggestion in suggestions:
            suggestion["_id"] = str(suggestion["_id"])
        
        return {
            "count": len(suggestions),
            "days": days,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch history: {str(e)}")

@router.put("/update/{suggestion_id}")
def update_suggestion_status(
    suggestion_id: str,
    data: AISuggestionUpdateSchema,
    user=Depends(admin_or_super_admin)
):
    """Update suggestion status (mark as read, implemented, or dismissed)"""
    try:
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = ai_suggestions_collection.update_one(
            {"_id": ObjectId(suggestion_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        return {"message": "Suggestion updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update suggestion: {str(e)}")

@router.get("/stats")
def get_suggestion_stats(user=Depends(admin_or_super_admin)):
    """Get statistics about AI suggestions"""
    try:
        total = ai_suggestions_collection.count_documents({"is_active": True})
        new = ai_suggestions_collection.count_documents({"status": "new", "is_active": True})
        read = ai_suggestions_collection.count_documents({"status": "read", "is_active": True})
        implemented = ai_suggestions_collection.count_documents({"status": "implemented", "is_active": True})
        dismissed = ai_suggestions_collection.count_documents({"status": "dismissed", "is_active": True})
        
        # Count by priority
        critical = ai_suggestions_collection.count_documents({"priority": "critical", "is_active": True})
        high = ai_suggestions_collection.count_documents({"priority": "high", "is_active": True})
        medium = ai_suggestions_collection.count_documents({"priority": "medium", "is_active": True})
        low = ai_suggestions_collection.count_documents({"priority": "low", "is_active": True})
        
        return {
            "total": total,
            "by_status": {
                "new": new,
                "read": read,
                "implemented": implemented,
                "dismissed": dismissed
            },
            "by_priority": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch stats: {str(e)}")
