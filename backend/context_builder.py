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
    """Build a concise transaction summary for agent context, filtered to 1 month from payday."""
    from datetime import timedelta
    
    bank_transactions = memory_data.get("bank_transactions", [])
    cash_transactions = memory_data.get("cash_transactions", [])
    
    if not bank_transactions and not cash_transactions:
        return {}
    
    # Get payday date from memory
    payday_info = memory_data.get("payday_info", {})
    last_payday_str = payday_info.get("last_payday")
    
    # Filter transactions to 1 month from payday
    filtered_transactions = []
    if last_payday_str:
        try:
            last_payday = datetime.fromisoformat(last_payday_str)
            one_month_later = last_payday + timedelta(days=30)
            
            for t in bank_transactions:
                tx_date_str = t.get("date")
                if tx_date_str:
                    try:
                        tx_date = datetime.fromisoformat(tx_date_str.split('T')[0])
                        if last_payday <= tx_date <= one_month_later:
                            filtered_transactions.append(t)
                    except:
                        filtered_transactions.append(t)
        except:
            filtered_transactions = bank_transactions
    else:
        # No payday set, use all transactions
        filtered_transactions = bank_transactions
    
    # Get recent transactions (last 20)
    recent = sorted(
        filtered_transactions,
        key=lambda t: t.get("date", ""),
        reverse=True
    )[:20]
    
    # Identify income transactions intelligently
    income_transactions = []
    expense_transactions = []
    
    for t in filtered_transactions:
        amount = t.get("amount", 0)
        name = t.get("name", "").lower()
        merchant = t.get("merchant_name", "").lower()
        category = t.get("category", [])
        
        # Income indicators: negative amount (Plaid convention) OR specific keywords
        is_income = (
            amount < 0 or  # Plaid uses negative for income
            "payroll" in name or
            "salary" in name or
            "direct deposit" in name or
            "income" in name or
            "payment from" in name or
            (isinstance(category, list) and any("income" in str(c).lower() for c in category))
        )
        
        if is_income:
            income_transactions.append(t)
        else:
            expense_transactions.append(t)
    
    # Calculate spending by category (expenses only)
    category_spending = {}
    total_spent = 0
    total_income = 0
    
    for t in income_transactions:
        total_income += abs(t.get("amount", 0))
    
    for t in expense_transactions:
        amount = abs(t.get("amount", 0))
        total_spent += amount
        cat = t.get("category", ["Other"])
        cat_name = cat[0] if isinstance(cat, list) and cat else "Other"
        category_spending[cat_name] = category_spending.get(cat_name, 0) + amount
    
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
    
    # Calculate current balance
    estimated_balance = total_income - total_spent
    
    # Calculate savings rate
    savings_rate = ((total_income - total_spent) / total_income * 100) if total_income > 0 else 0
    
    return {
        "recent_transactions": [
            {
                "date": t.get("date"),
                "merchant": t.get("merchant_name", t.get("name", "Unknown")),
                "amount": t.get("amount"),
                "category": t.get("category", ["Other"])[0] if isinstance(t.get("category"), list) else t.get("category", "Other"),
                "type": "income" if t in income_transactions else "expense"
            }
            for t in recent[:10]  # Only include top 10 for prompt brevity
        ],
        "spending_by_category": top_categories,
        "total_spent": round(total_spent, 2),
        "total_income": round(total_income, 2),
        "estimated_balance": round(estimated_balance, 2),
        "savings_rate": round(savings_rate, 2),
        "income_transaction_count": len(income_transactions),
        "expense_transaction_count": len(expense_transactions),
        "transaction_count": len(filtered_transactions) + len(cash_transactions),
        "cash_transaction_count": len(cash_transactions),
        "period": f"1 month from payday ({last_payday_str.split('T')[0] if last_payday_str else 'all time'})"
    }
