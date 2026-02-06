from fastapi import FastAPI
from router import Router
from memory.memory_manager import MemoryManager
from personality.tone_engine import determine_tone, ToneEngine
from context_builder import build_context
from datetime import datetime

app = FastAPI()

router = Router()
memory = MemoryManager()
tone_engine = ToneEngine()


@app.post("/chat")
def chat(payload: dict):

    user_id = payload["user_id"]
    message = payload["message"]
    personality = payload.get("personality")
    
    # Check if user is reporting payday
    is_payday_report = payload.get("is_payday", False)

    memory_data = memory.load(user_id)
    
    # Handle payday reporting
    if is_payday_report:
        payday_date = datetime.now()
        # Update payday info in memory
        memory_data = tone_engine.update_payday_info(memory_data, payday_date, 0)

    # Enhanced tone determination with message analysis
    tone = determine_tone(personality, memory_data, message)

    context = build_context(user_id, memory_data, tone, message)

    agent_used, result = router.dispatch(message, context)

    # Update memory with tone preference and interaction history
    if "interaction_history" not in memory_data:
        memory_data["interaction_history"] = []
    
    memory_data["interaction_history"].append({
        "tone": tone,
        "agent": agent_used,
        "timestamp": context["date"]
    })
    
    # Keep only last 50 interactions
    if len(memory_data["interaction_history"]) > 50:
        memory_data["interaction_history"] = memory_data["interaction_history"][-50:]
    
    # Save preferred tone if user explicitly set it
    if personality:
        memory_data["preferred_tone"] = personality
    
    # Save updated context
    memory.save(user_id, memory_data)
    context["memory"] = memory_data  # Update context with latest memory

    # Include payday effect in response if detected
    payday_effect = context.get("payday_effect")
    
    response_data = {
        "agent_used": agent_used,
        "response": result,
        "tone": tone,
        "tone_description": context.get("tone_description", ""),
        "date_context": context.get("date_context", {})
    }
    
    # Add payday effect warnings and suggestions
    if payday_effect:
        response_data["payday_effect"] = {
            "warning": payday_effect.get("warning_message"),
            "suggestion": payday_effect.get("suggestion"),
            "days_since_payday": payday_effect.get("days_since_payday"),
            "average_overspend": payday_effect.get("average_overspend")
        }
    
    return response_data
