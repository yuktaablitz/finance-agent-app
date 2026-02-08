from fastapi import FastAPI, UploadFile, File, HTTPException
from router import Router
from memory.memory_manager import MemoryManager
from personality.tone_engine import determine_tone, ToneEngine
from context_builder import build_context
from datetime import datetime
from uuid import uuid4
import json
from pathlib import Path

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


@app.post("/upload-receipt")
async def upload_receipt(user_id: str, image: UploadFile = File(...)):
    """Upload a receipt/cash transaction image and store the extracted transaction in memory."""
    try:
        image_bytes = await image.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image upload")

        # Lazy import so /chat still works even if Gemini config isn't set during early dev.
        from models.gemini_client import GeminiClient

        client = GeminiClient()
        extracted = client.extract_transaction_from_receipt(
            image_bytes=image_bytes,
            mime_type=image.content_type or "image/jpeg",
        )

        tx = {
            "id": str(uuid4()),
            "source": "receipt_upload",
            "uploaded_at": datetime.now().isoformat(),
            **(extracted or {}),
        }

        memory_data = memory.load(user_id)
        if "cash_transactions" not in memory_data:
            memory_data["cash_transactions"] = []
        memory_data["cash_transactions"].append(tx)
        memory.save(user_id, memory_data)

        return {"status": "ok", "transaction": tx}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Receipt processing failed: {str(e)}")


@app.post("/load-transactions")
def load_transactions(user_id: str, file_path: str = "/Users/blitz/Documents/finance-agent-app/transaction_data.json"):
    """Load transaction data from JSON file into user memory for demo purposes."""
    try:
        json_path = Path(file_path)
        if not json_path.exists():
            raise HTTPException(status_code=404, detail=f"Transaction file not found: {file_path}")
        
        with open(json_path, 'r') as f:
            transactions = json.load(f)
        
        if not isinstance(transactions, list):
            raise HTTPException(status_code=400, detail="Expected JSON array of transactions")
        
        memory_data = memory.load(user_id)
        memory_data["bank_transactions"] = transactions
        memory_data["transactions_loaded_at"] = datetime.now().isoformat()
        memory.save(user_id, memory_data)
        
        # Calculate summary stats
        total_spent = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
        total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
        categories = {}
        for t in transactions:
            if t["amount"] < 0:  # Only count expenses
                cat = t["category"][0] if isinstance(t["category"], list) and t["category"] else "Other"
                categories[cat] = categories.get(cat, 0) + abs(t["amount"])
        
        return {
            "status": "ok",
            "transactions_loaded": len(transactions),
            "total_spent": round(total_spent, 2),
            "total_income": round(total_income, 2),
            "top_categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load transactions: {str(e)}")


@app.get("/get-transactions/{user_id}")
def get_transactions(user_id: str, limit: int = 20):
    """Get loaded transactions for a user (for debugging/demo)."""
    memory_data = memory.load(user_id)
    transactions = memory_data.get("bank_transactions", [])
    cash_transactions = memory_data.get("cash_transactions", [])
    
    return {
        "bank_transactions": transactions[:limit],
        "cash_transactions": cash_transactions,
        "total_bank_transactions": len(transactions),
        "total_cash_transactions": len(cash_transactions)
    }
