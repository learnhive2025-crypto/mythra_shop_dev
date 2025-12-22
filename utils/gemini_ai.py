import os
from typing import Dict, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiAI:
    """Wrapper for Google Gemini AI model"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.enabled = True
        else:
            self.enabled = False
            print("⚠️ Gemini API key not configured. Using rule-based suggestions.")
    
    def generate_business_suggestions(self, business_data: Dict) -> List[Dict]:
        """
        Use Gemini AI to generate intelligent business suggestions
        
        Args:
            business_data: Dictionary containing sales, inventory, and expense data
        
        Returns:
            List of suggestion dictionaries
        """
        if not self.enabled:
            return []
        
        try:
            # Create a detailed prompt for Gemini
            prompt = f"""
You are a business consultant AI analyzing a retail shop's data. Based on the following business metrics, provide 3-5 actionable business suggestions.

**Sales Data:**
- Monthly Revenue: ₹{business_data['sales']['monthly_revenue']:.2f}
- Weekly Revenue: ₹{business_data['sales']['weekly_revenue']:.2f}
- Total Sales Count: {business_data['sales']['total_sales_count']}
- Top Selling Products: {business_data['sales']['top_products'][:3]}

**Inventory Data:**
- Total Products: {business_data['inventory']['total_products']}
- Low Stock Items: {business_data['inventory']['low_stock_count']}
- Out of Stock Items: {business_data['inventory']['out_of_stock_count']}
- Overstocked Items: {business_data['inventory']['overstocked_count']}

**Expense Data:**
- Monthly Expenses: ₹{business_data['expenses']['monthly_expenses']:.2f}
- Expense Categories: {business_data['expenses']['top_categories']}

**Instructions:**
1. Analyze the data for patterns, risks, and opportunities
2. Provide specific, actionable suggestions
3. Prioritize suggestions by impact (critical, high, medium, low)
4. Focus on: inventory optimization, revenue growth, cost reduction, customer retention

**Response Format (JSON):**
Return ONLY a valid JSON array of suggestions, each with:
- "type": "sales" | "inventory" | "expense" | "marketing" | "operations"
- "title": Brief title with emoji
- "description": Detailed actionable advice (2-3 sentences)
- "priority": "critical" | "high" | "medium" | "low"
- "expected_impact": Brief description of expected outcome

Example:
[
  {{
    "type": "inventory",
    "title": "🚨 Urgent: Restock Critical Items",
    "description": "You have 5 products out of stock. Prioritize restocking your top sellers to avoid losing customers to competitors.",
    "priority": "critical",
    "expected_impact": "Prevent revenue loss of ₹10,000-15,000"
  }}
]
"""
            
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            import json
            import re
            
            # Extract JSON from response
            text = response.text
            # Try to find JSON array in the response
            json_match = re.search(r'\[[\s\S]*\]', text)
            if json_match:
                suggestions = json.loads(json_match.group())
                return suggestions
            else:
                print("⚠️ Could not parse AI response as JSON")
                return []
                
        except Exception as e:
            print(f"⚠️ Gemini AI error: {str(e)}")
            return []
