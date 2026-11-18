# Finance Agent App

A multi-agent personal-finance assistant API. One `/chat` endpoint routes each message to a specialist agent
(spending, budgeting, investing or general), adapts its tone to the user, remembers past interactions, and warns about
the "payday effect" (overspending in the days right after payday).

## How it works

```
POST /chat ──▶ MemoryManager.load(user_id)
           ──▶ ToneEngine: zen_coach | tough_love | supportive (user choice, saved preference, or message cues)
           ──▶ build_context: memory, tone, date context, payday-effect check
           ──▶ Router.classify_intent ──▶ SpendingAgent | BudgetingAgent | InvestingAgent | GeneralAgent
           ──▶ agent prompt ──▶ Gemini (GeminiClient)
           ──▶ MemoryManager.save (last 50 interactions, preferred tone)
```

- **Intent routing** (`backend/router.py`): keyword-based for now (`spend`/`expense`, `budget`, `invest`/`stock`,
  otherwise general). The router is the single place to swap in an LLM classifier.
- **Tone engine** (`backend/personality/tone_engine.py`): three personalities plus payday tracking. Send
  `"is_payday": true` to record a payday; later requests within 3 days get a warning and a suggestion if past spending
  after payday ran high.
- **Memory** (`backend/memory/memory_manager.py`): in-process dictionary keyed by `user_id` (resets when the server restarts).
- **LLM** (`backend/models/gemini_client.py`): calls Gemini when `GEMINI_API_KEY` is set; otherwise runs in stub
  mode and echoes the prompt, so everything else works with no key.

## Run it

Requires Python 3.10+.

```bash
git clone https://github.com/yuktaablitz/finance-agent-app.git
cd finance-agent-app/backend
python3 -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # optional: add GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs

```bash
curl -s localhost:8000/chat -H 'Content-Type: application/json' \
  -d '{"user_id": "demo", "message": "Help me budget for next month", "personality": "tough_love"}'

# record a payday
curl -s localhost:8000/chat -H 'Content-Type: application/json' \
  -d '{"user_id": "demo", "message": "Just got paid", "is_payday": true}'
```

Request fields: `user_id` (required), `message` (required), `personality` (`zen_coach`, `tough_love` or
`supportive`, optional), `is_payday` (optional).

Response fields: `agent_used`, `response`, `tone`, `tone_description`, `date_context`, and `payday_effect` when one is detected.

## Project layout

```
backend/
  main.py               FastAPI app, /chat endpoint
  router.py             intent classification + dispatch to agents
  context_builder.py    builds the prompt context (memory, tone, dates, payday effect)
  agents/               spending, budgeting, investing, general agents
  personality/          tone engine and payday-effect detection
  memory/               per-user memory store
  models/               Gemini client
  schemas/              response models
```

## Next steps

- Replace keyword routing with an LLM intent classifier.
- Persist memory in Redis or a database instead of process memory.
- Add tests for routing and the payday effect.

## Tech stack

Python, FastAPI, Pydantic, Google Gemini API (`google-genai`), Uvicorn.
