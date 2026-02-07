from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from router import Router
from memory.memory_manager import MemoryManager
from personality.tone_engine import determine_tone
from context_builder import build_context


app = FastAPI()

router = Router()
memory = MemoryManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
def chat(payload: dict):

    user_id = payload["user_id"]
    message = payload["message"]
    personality = payload.get("personality")

    memory_data = memory.load(user_id)

    tone = determine_tone(personality, memory_data)

    context = build_context(user_id, memory_data, tone)

    agent_used, result = router.dispatch(message, context)

    memory.save(user_id, context)

    return {
        "agent_used": agent_used,
        "response": result,
        "tone": tone
    }
