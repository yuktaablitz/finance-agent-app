"""
FastAPI Application - Main Entry Point
Unified Agent API with standardized JSON responses
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from models.agent_models import AgentQuery, AgentResponse, UserContext, FinancialPersonality
from agents.unified_agent import unified_agent
from services.gemini_service import gemini_service
from schemas.responses import format_json_response, format_error_response


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
    description="AI-powered personal finance companion with unified agent routing",
    version="1.0.0",
    lifespan=lifespan
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


@app.get("/gemini/models")
async def list_gemini_models():
    """Debug endpoint: list Gemini models available for the configured API key."""
    try:
        return await gemini_service.list_available_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list Gemini models: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check."""
    try:
        gemini_status = gemini_service.get_service_status()
        response_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "agents_available": ["spending", "investing", "savings", "budget"],
            "personalities": ["zen", "tough_love", "to_the_point", "no_bs", "supportive"],
            "services": {
                "gemini": gemini_status
            }
        }
        return format_json_response(response_data)
    except Exception as e:
        error_data = {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "agents_available": ["spending", "investing", "savings", "budget"],
            "personalities": ["zen", "tough_love", "to_the_point", "no_bs", "supportive"]
        }
        return format_json_response(error_data, status_code=500)


@app.post("/agent/chat", response_model=AgentResponse)
async def agent_chat(query: AgentQuery):
    """
    Main agent chat endpoint.
    
    - Single agent bar routes to specialized sub-agents
    - Returns standardized JSON format
    - Maintains session state across agent switches
    - Supports financial personality customization
    
    Response format:
    {
        "response": "natural language advice",
        "metadata": {
            "agent": "spending",
            "confidence": 0.92,
            "personality_used": "tough_love",
            "context_factors": ["3 days until payday", "low balance"],
            "suggested_action": "wait_until_payday",
            "related_transactions": ["txn_001"]
        }
    }
    """
    try:
        response = await unified_agent.process_query(query)
        return format_json_response(response.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/agent/session/{session_id}")
async def get_session_summary(session_id: str):
    """Get summary of agent session history."""
    summary = unified_agent.get_session_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Session not found")
    return format_json_response(summary)


@app.get("/personalities")
async def get_personalities():
    """Get available financial personality options."""
    personalities_data = {
        "zen": {
            "name": "Zen",
            "description": "Calm, mindful, encouraging long-term perspective",
            "tone": "Peaceful and reflective"
        },
        "tough_love": {
            "name": "Tough Love",
            "description": "Direct, challenging, pushes you to do better",
            "tone": "Honest and motivating"
        },
        "to_the_point": {
            "name": "To The Point",
            "description": "Brief, factual, minimal explanation",
            "tone": "Concise and direct"
        },
        "no_bs": {
            "name": "No BS",
            "description": "Blunt, data-driven, cuts through excuses",
            "tone": "Direct and factual"
        },
        "supportive": {
            "name": "Supportive",
            "description": "Encouraging, educational, builds confidence",
            "tone": "Warm and helpful"
        }
    }
    return format_json_response(personalities_data)


@app.post("/agent/chat/example")
async def example_chat():
    """Example endpoint showing proper request format."""
    example_query = AgentQuery(
        query="Should I buy this $200 jacket?",
        user_context=UserContext(
            user_id="example_user",
            financial_personality=FinancialPersonality.TOUGH_LOVE,
            payday_day=15,
            monthly_income=5000.0,
            current_balance=1200.0,
            monthly_budget=4000.0
        ),
        session_id="example_session_123",
        transaction_context=[
            {
                "id": "txn_001",
                "amount": 45.67,
                "category": "food",
                "merchant": "Chipotle",
                "date": "2024-02-01T12:00:00Z",
                "type": "debit"
            },
            {
                "id": "txn_002", 
                "amount": 89.99,
                "category": "shopping",
                "merchant": "Nike",
                "date": "2024-02-03T15:30:00Z",
                "type": "debit"
            }
        ]
    )
    
    response = await unified_agent.process_query(example_query)
    return format_json_response({
        "example_request": example_query.model_dump(),
        "response": response.model_dump()
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
