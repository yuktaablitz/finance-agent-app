"""FastAPI application entry point.

This app keeps the legacy `POST /chat` endpoint stable for the Flutter client,
while optionally routing internally to the newer unified agent router when
available/configured.
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router import Router
from memory.memory_manager import MemoryManager
from personality.tone_engine import determine_tone, ToneEngine
from context_builder import build_context


router = Router()
memory = MemoryManager()
tone_engine = ToneEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Finance Agent API...")
    yield
    # Shutdown
    print("🛑 Shutting down Finance Agent API...")


app = FastAPI(
    title="Finance Agent API",
    description="AI-powered personal finance companion",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Finance Agent API",
        "version": "1.0.0"
    }


def _run_async(coro):
    """Run an async coroutine from sync context safely."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # If we're already in an event loop, create a new task and wait.
        import concurrent.futures

        fut: concurrent.futures.Future = asyncio.run_coroutine_threadsafe(coro, loop)
        return fut.result()

    return asyncio.run(coro)


def _map_tone_to_financial_personality(tone: Optional[str]):
    # Lazy import: models exist only if feature/agents is merged.
    from models.agent_models import FinancialPersonality

    if not tone:
        return FinancialPersonality.SUPPORTIVE

    t = str(tone).strip().lower()
    mapping = {
        "zen": FinancialPersonality.ZEN,
        "zen_coach": FinancialPersonality.ZEN,
        "tough": FinancialPersonality.TOUGH_LOVE,
        "tough_love": FinancialPersonality.TOUGH_LOVE,
        "support": FinancialPersonality.SUPPORTIVE,
        "supportive": FinancialPersonality.SUPPORTIVE,
        "to_the_point": FinancialPersonality.TO_THE_POINT,
        "no_bs": FinancialPersonality.NO_BS,
    }
    return mapping.get(t, FinancialPersonality.SUPPORTIVE)


@app.post("/chat")
async def chat(payload: Dict[str, Any]):
    user_id = payload["user_id"]
    message = payload["message"]
    personality = payload.get("personality")

    # Check if user is reporting payday
    is_payday_report = payload.get("is_payday", False)

    memory_data = memory.load(user_id)

    # Handle payday reporting
    if is_payday_report:
        payday_date = datetime.now()
        memory_data = tone_engine.update_payday_info(memory_data, payday_date, 0)

    # Enhanced tone determination with message analysis
    tone = determine_tone(personality, memory_data, message)

    context = build_context(user_id, memory_data, tone, message)

    # Prefer the unified agent router (feature/agents). Fall back to legacy router.
    agent_used: str
    result: Dict[str, Any]
    try:
        from models.agent_models import AgentQuery, UserContext
        from agents.unified_agent import unified_agent

        user_ctx = UserContext(
            user_id=str(user_id),
            financial_personality=_map_tone_to_financial_personality(tone),
        )
        query = AgentQuery(
            query=message,
            user_context=user_ctx,
            session_id=payload.get("session_id"),
            transaction_context=payload.get("transaction_context"),
        )

        agent_response = await unified_agent.process_query(query)
        agent_used = getattr(agent_response.metadata, "agent", "general")
        result = agent_response.model_dump()
    except Exception:
        agent_used, result = router.dispatch(message, context)

    # Update memory with tone preference and interaction history
    if "interaction_history" not in memory_data:
        memory_data["interaction_history"] = []

    memory_data["interaction_history"].append(
        {
            "tone": tone,
            "agent": agent_used,
            "timestamp": context["date"],
        }
    )

    # Keep only last 50 interactions
    if len(memory_data["interaction_history"]) > 50:
        memory_data["interaction_history"] = memory_data["interaction_history"][-50:]

    # Save preferred tone if user explicitly set it
    if personality:
        memory_data["preferred_tone"] = personality

    memory.save(user_id, memory_data)
    context["memory"] = memory_data

    payday_effect = context.get("payday_effect")

    response_data: Dict[str, Any] = {
        "agent_used": agent_used,
        "response": result,
        "tone": tone,
        "tone_description": context.get("tone_description", ""),
        "date_context": context.get("date_context", {}),
    }

    if payday_effect:
        response_data["payday_effect"] = {
            "warning": payday_effect.get("warning_message"),
            "suggestion": payday_effect.get("suggestion"),
            "days_since_payday": payday_effect.get("days_since_payday"),
            "average_overspend": payday_effect.get("average_overspend"),
        }

    return response_data
