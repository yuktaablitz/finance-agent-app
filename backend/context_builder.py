# context_builder.py

from datetime import datetime
from personality.tone_engine import ToneEngine


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
    
    return context
