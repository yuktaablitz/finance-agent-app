# context_builder.py

from datetime import datetime
from personality.tone_engine import ToneEngine
from typing import Dict, List, Any


def build_context(user_id: str, memory_data: dict, tone: str, message: str = None) -> dict:
    """
    Combines memory + date awareness + tone + payday detection into unified context.
    """
    
    today = datetime.now()
    engine = ToneEngine()
    
    # Get date context
    date_context = engine.get_date_context(today)
    
    # Detect payday effect
    payday_effect = engine.detect_payday_effect(memory_data, today)
    
    # Build comprehensive context
    context = {
        "user_id": user_id,
        "date": today.isoformat(),
        "date_context": date_context,
        "memory": memory_data,
        "tone": tone,
        "tone_description": engine.get_tone_description(tone),
        "message": message,
        "payday_effect": payday_effect  # Payday detection info
    }
    
    # Add financial context if available
    if memory_data:
        if "budget_status" in memory_data:
            context["budget_status"] = memory_data["budget_status"]
        if "recent_spending" in memory_data:
            context["spending_trend"] = memory_data.get("recent_spending", {})
    
    # Add transaction context for data-driven advice
    transaction_summary = _build_transaction_summary(memory_data)
    if transaction_summary:
        context["transaction_summary"] = transaction_summary
    
    return context


def _build_transaction_summary(memory_data: Dict) -> Dict[str, Any]:
    """Build a concise transaction summary for agent context."""
    bank_transactions = memory_data.get("bank_transactions", [])
    cash_transactions = memory_data.get("cash_transactions", [])
    
    if not bank_transactions and not cash_transactions:
        return {}
    
    # Get recent transactions (last 20)
    recent = sorted(
        bank_transactions,
        key=lambda t: t.get("date", ""),
        reverse=True
    )[:20]
    
    # Calculate spending by category
    category_spending = {}
    total_spent = 0
    total_income = 0
    
    for t in bank_transactions:
        amount = t.get("amount", 0)
        if amount < 0:
            total_spent += abs(amount)
            cat = t.get("category", ["Other"])
            cat_name = cat[0] if isinstance(cat, list) and cat else "Other"
            category_spending[cat_name] = category_spending.get(cat_name, 0) + abs(amount)
        elif amount > 0:
            total_income += amount
    
    # Add cash transactions to spending
    for t in cash_transactions:
        amount = t.get("amount", 0)
        if amount:
            total_spent += abs(amount)
            cat = t.get("category", "Cash")
            category_spending[cat] = category_spending.get(cat, 0) + abs(amount)
    
    # Get top spending categories
    top_categories = dict(sorted(
        category_spending.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5])
    
    # Estimate current balance (last income - total spent)
    estimated_balance = total_income - total_spent
    
    return {
        "recent_transactions": [
            {
                "date": t.get("date"),
                "merchant": t.get("merchant_name", t.get("name", "Unknown")),
                "amount": t.get("amount"),
                "category": t.get("category", ["Other"])[0] if isinstance(t.get("category"), list) else t.get("category", "Other")
            }
            for t in recent[:10]  # Only include top 10 for prompt brevity
        ],
        "spending_by_category": top_categories,
        "total_spent": round(total_spent, 2),
        "total_income": round(total_income, 2),
        "estimated_balance": round(estimated_balance, 2),
        "transaction_count": len(bank_transactions) + len(cash_transactions),
        "cash_transaction_count": len(cash_transactions)
    }
