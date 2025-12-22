from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from database import db
from schemas.expense_schema import ExpenseCreateSchema, ExpenseUpdateSchema
from models.expense_model import expense_model
from utils.security import admin_or_super_admin

# Collection
expenses_collection = db["expenses"]

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)

@router.post("/add")
def add_expense(
    data: ExpenseCreateSchema,
    user=Depends(admin_or_super_admin)
):
    try:
        # If date is not provided, use today's date in YYYY-MM-DD
        expense_date = data.date if data.date else datetime.utcnow().strftime("%Y-%m-%d")
        
        new_expense = expense_model(
            date=expense_date,
            category=data.category,
            amount=data.amount,
            description=data.description
        )
        
        expenses_collection.insert_one(new_expense)
        
        return {"message": "Expense added successfully", "date": expense_date}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add expense: {str(e)}")

@router.get("/list")
def list_expenses(user=Depends(admin_or_super_admin)):
    try:
        expenses = list(expenses_collection.find({"is_active": True}))
        for expense in expenses:
            expense["_id"] = str(expense["_id"])
        return expenses
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch expenses: {str(e)}")

@router.get("/{id}")
def get_expense(id: str, user=Depends(admin_or_super_admin)):
    try:
        expense_oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid expense ID")

    expense = expenses_collection.find_one({"_id": expense_oid, "is_active": True})
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    expense["_id"] = str(expense["_id"])
    return expense

@router.put("/update/{id}")
def update_expense(
    id: str, 
    data: ExpenseUpdateSchema, 
    user=Depends(admin_or_super_admin)
):
    try:
        expense_oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid expense ID")

    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = expenses_collection.update_one(
        {"_id": expense_oid, "is_active": True},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    return {"message": "Expense updated successfully"}

@router.delete("/delete/{id}")
def delete_expense(id: str, user=Depends(admin_or_super_admin)):
    try:
        expense_oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid expense ID")

    result = expenses_collection.update_one(
        {"_id": expense_oid, "is_active": True},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    return {"message": "Expense deleted successfully"}
