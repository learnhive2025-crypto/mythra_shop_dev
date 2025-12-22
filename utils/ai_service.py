from datetime import datetime, timedelta
from database import db
from typing import List, Dict

products_collection = db["products"]
sales_collection = db["sales"]
purchases_collection = db["purchases"]
expenses_collection = db["expenses"]

class AIBusinessAnalyzer:
    """AI-powered business analysis and suggestion generator"""
    
    @staticmethod
    def analyze_sales_trends() -> Dict:
        """Analyze sales patterns and trends"""
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Weekly sales
        weekly_sales = list(sales_collection.find({"created_at": {"$gte": week_ago}}))
        weekly_revenue = sum(s.get("total_amount", 0) for s in weekly_sales)
        
        # Monthly sales
        monthly_sales = list(sales_collection.find({"created_at": {"$gte": month_ago}}))
        monthly_revenue = sum(s.get("total_amount", 0) for s in monthly_sales)
        
        # Product performance
        product_sales = {}
        for sale in monthly_sales:
            for item in sale.get("items", []):
                pid = item["product_id"]
                product_sales[pid] = product_sales.get(pid, 0) + item["qty"]
        
        return {
            "weekly_revenue": weekly_revenue,
            "monthly_revenue": monthly_revenue,
            "total_sales_count": len(monthly_sales),
            "top_products": sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    @staticmethod
    def analyze_inventory() -> Dict:
        """Analyze inventory levels and stock issues"""
        low_stock_threshold = 10
        
        products = list(products_collection.find({"is_active": True}))
        
        low_stock = [p for p in products if p.get("stock_qty", 0) < low_stock_threshold]
        out_of_stock = [p for p in products if p.get("stock_qty", 0) == 0]
        overstocked = [p for p in products if p.get("stock_qty", 0) > 100]
        
        return {
            "total_products": len(products),
            "low_stock_count": len(low_stock),
            "out_of_stock_count": len(out_of_stock),
            "overstocked_count": len(overstocked),
            "low_stock_items": [{"name": p["name"], "qty": p.get("stock_qty", 0)} for p in low_stock[:5]]
        }
    
    @staticmethod
    def analyze_expenses() -> Dict:
        """Analyze expense patterns"""
        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)
        
        # Get monthly expenses
        monthly_expenses = list(expenses_collection.find({
            "is_active": True,
            "created_at": {"$gte": month_ago}
        }))
        
        total_expenses = sum(e.get("amount", 0) for e in monthly_expenses)
        
        # Category breakdown
        category_expenses = {}
        for expense in monthly_expenses:
            cat = expense.get("category", "Other")
            category_expenses[cat] = category_expenses.get(cat, 0) + expense.get("amount", 0)
        
        return {
            "monthly_expenses": total_expenses,
            "expense_count": len(monthly_expenses),
            "top_categories": sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    @staticmethod
    def generate_suggestions() -> List[Dict]:
        """Generate AI-powered business suggestions"""
        suggestions = []
        
        # Analyze data
        sales_data = AIBusinessAnalyzer.analyze_sales_trends()
        inventory_data = AIBusinessAnalyzer.analyze_inventory()
        expense_data = AIBusinessAnalyzer.analyze_expenses()
        
        # Try to use Gemini AI first
        try:
            from utils.gemini_ai import GeminiAI
            
            gemini = GeminiAI()
            if gemini.enabled:
                business_data = {
                    "sales": sales_data,
                    "inventory": inventory_data,
                    "expenses": expense_data
                }
                
                ai_suggestions = gemini.generate_business_suggestions(business_data)
                
                # If AI generated suggestions, use them
                if ai_suggestions:
                    return ai_suggestions
        except Exception as e:
            print(f"⚠️ AI generation failed, using rule-based: {str(e)}")
        
        # Fallback to rule-based suggestions
        # Suggestion 1: Low Stock Alert
        if inventory_data["low_stock_count"] > 0:
            low_stock_names = ", ".join([item["name"] for item in inventory_data["low_stock_items"][:3]])
            suggestions.append({
                "type": "inventory",
                "title": f"⚠️ {inventory_data['low_stock_count']} Products Running Low on Stock",
                "description": f"Products like {low_stock_names} are running low. Consider restocking to avoid lost sales opportunities.",
                "priority": "high",
                "data_insights": {
                    "low_stock_count": inventory_data["low_stock_count"],
                    "items": inventory_data["low_stock_items"]
                }
            })
        
        # Suggestion 2: Out of Stock Critical
        if inventory_data["out_of_stock_count"] > 0:
            suggestions.append({
                "type": "inventory",
                "title": f"🚨 {inventory_data['out_of_stock_count']} Products Out of Stock",
                "description": "You have products with zero inventory. Restock immediately to prevent customer disappointment and lost revenue.",
                "priority": "critical",
                "data_insights": {
                    "out_of_stock_count": inventory_data["out_of_stock_count"]
                }
            })
        
        # Suggestion 3: Sales Performance
        if sales_data["monthly_revenue"] > 0:
            avg_daily_revenue = sales_data["monthly_revenue"] / 30
            suggestions.append({
                "type": "sales",
                "title": f"📊 Monthly Revenue: ₹{sales_data['monthly_revenue']:.2f}",
                "description": f"Your average daily revenue is ₹{avg_daily_revenue:.2f}. Focus on upselling and cross-selling to increase this metric.",
                "priority": "medium",
                "data_insights": {
                    "monthly_revenue": sales_data["monthly_revenue"],
                    "avg_daily": avg_daily_revenue,
                    "total_sales": sales_data["total_sales_count"]
                }
            })
        
        # Suggestion 4: Expense Management
        if expense_data["monthly_expenses"] > 0:
            expense_ratio = (expense_data["monthly_expenses"] / sales_data["monthly_revenue"] * 100) if sales_data["monthly_revenue"] > 0 else 0
            
            if expense_ratio > 50:
                suggestions.append({
                    "type": "expense",
                    "title": f"💰 High Expense Ratio: {expense_ratio:.1f}%",
                    "description": f"Your expenses are {expense_ratio:.1f}% of revenue. Consider reviewing and optimizing costs to improve profitability.",
                    "priority": "high",
                    "data_insights": {
                        "expense_ratio": expense_ratio,
                        "total_expenses": expense_data["monthly_expenses"],
                        "top_categories": expense_data["top_categories"]
                    }
                })
            else:
                suggestions.append({
                    "type": "expense",
                    "title": f"✅ Healthy Expense Ratio: {expense_ratio:.1f}%",
                    "description": f"Your expense management is good. Keep monitoring to maintain this healthy ratio.",
                    "priority": "low",
                    "data_insights": {
                        "expense_ratio": expense_ratio,
                        "total_expenses": expense_data["monthly_expenses"]
                    }
                })
        
        # Suggestion 5: Top Products Promotion
        if sales_data["top_products"]:
            top_product_ids = [pid for pid, _ in sales_data["top_products"][:3]]
            suggestions.append({
                "type": "marketing",
                "title": "🎯 Promote Your Best Sellers",
                "description": "Your top-selling products are performing well. Consider creating bundle offers or loyalty rewards around these items.",
                "priority": "medium",
                "data_insights": {
                    "top_products": sales_data["top_products"][:3]
                }
            })
        
        # Suggestion 6: Overstocked Items
        if inventory_data["overstocked_count"] > 0:
            suggestions.append({
                "type": "inventory",
                "title": f"📦 {inventory_data['overstocked_count']} Overstocked Products",
                "description": "Some products have high inventory levels. Consider running promotions or discounts to move excess stock.",
                "priority": "medium",
                "data_insights": {
                    "overstocked_count": inventory_data["overstocked_count"]
                }
            })
        
        return suggestions
