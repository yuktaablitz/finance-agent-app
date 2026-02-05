# context_builder.py

from datetime import datetime


def build_context(user_id: str, memory_data: dict, tone: str) -> dict:
    """
    Combines memory + date awareness + tone into unified context.
    """

    today = datetime.now()

    context = {
        "user_id": user_id,
        "date": today.isoformat(),
        "memory": memory_data,
        "tone": tone
    }

    return context
