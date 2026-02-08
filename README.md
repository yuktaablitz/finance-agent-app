# AccountantAI - Gemini-Powered Personal Finance Companion 🎯

AI-powered personal finance assistant with context-aware reasoning, multi-agent architecture, and dynamic personality engine.

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# Install dependencies
pip install fastapi uvicorn google-generativeai python-dotenv

# Set your Gemini API key
export GEMINI_API_KEY=your_key_here

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Load Your Transaction Data

```bash
# Load the 500 synthetic transactions
curl -X POST "http://localhost:8000/load-transactions?user_id=demo_user_123"
```

### Test the Chat

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Should I buy a $200 jacket?",
    "personality": "tough_love"
  }'
```

## 📋 API Endpoints

### Core Endpoints

- **`POST /chat`** - Main chat interface with context-aware agents
  - Supports personalities: `zen_coach`, `tough_love`, `supportive`, `to_the_point`, `no_bs`
  - Returns agent routing, response, tone, and financial context

- **`POST /load-transactions`** - Load transaction data from JSON
  - Default path: `/Users/blitz/Documents/finance-agent-app/transaction_data.json`
  - Returns summary stats and top spending categories

- **`POST /upload-receipt`** - Upload receipt image for Gemini extraction
  - Multimodal processing with Gemini
  - Extracts: amount, merchant, date, category, description
  - Stores in user memory as cash transaction

- **`GET /get-transactions/{user_id}`** - View loaded transactions (debugging)

### Health & Debug

- **`GET /`** - Health check
- **`GET /health`** - Detailed service status

## 🎭 Financial Personalities

- **Zen Coach**: Calm, mindful, long-term perspective
- **Tough Love**: Direct, challenging, pushes you to do better
- **Supportive**: Encouraging, educational, builds confidence
- **To The Point**: Brief, factual, minimal explanation
- **No BS**: Blunt, data-driven, cuts through excuses

## 🧠 Multi-Agent Architecture

```
User Query
    ↓
Router Agent (Gemini-powered intent classification)
    ↓
┌─────────────┬──────────────┬──────────────┬──────────────┐
│  Spending   │  Budgeting   │  Investing   │   General    │
│   Agent     │    Agent     │    Agent     │    Agent     │
└─────────────┴──────────────┴──────────────┴──────────────┘
    ↓
Personality Engine (tone adjustment)
    ↓
Gemini API (reasoning + advice)
    ↓
Response with metadata
```

## 🔥 Key Features

### Context-Aware Reasoning
- Agents analyze your actual transaction history
- Spending patterns by category
- Balance tracking
- Payday effect detection

### Multimodal Receipt Understanding
- Upload cash receipts
- Gemini extracts structured transaction data
- Automatically categorizes and stores

### Dynamic Personality
- Choose your preferred financial advisor style
- Tone adapts to spending behavior
- Consistent personality across sessions

### Transaction Data Integration
- Load 500+ synthetic transactions
- Real-time spending analysis
- Category-based insights
- Balance estimation

## 📊 Transaction Data Schema

```json
{
  "transaction_id": "tx_001",
  "date": "2025-10-31",
  "name": "STARBUCKS STORE 09221",
  "amount": -5.95,
  "category": ["Food and Drink", "Coffee Shop"],
  "merchant_name": "Starbucks",
  "payment_channel": "in store"
}
```

## 🎬 Demo Script for Judges

### 1. Show Data Loading
```bash
curl -X POST "http://localhost:8000/load-transactions?user_id=demo_user_123"
```
**Highlight**: "We've loaded 500 synthetic transactions representing a month of financial activity"

### 2. Context-Aware Chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Can I afford to eat out tonight?",
    "personality": "tough_love"
  }'
```
**Highlight**: "Notice how the agent references actual spending data - categories, amounts, balance"

### 3. Personality Switching
Test with different personalities on the same question:
- `zen_coach` - Calm, reflective
- `tough_love` - Direct, challenging
- `supportive` - Encouraging

**Highlight**: "Same financial data, different communication styles"

### 4. Receipt Upload
```bash
curl -X POST "http://localhost:8000/upload-receipt?user_id=demo_user_123" \
  -F "image=@receipt.jpg"
```
**Highlight**: "Gemini multimodal extracts transaction details from images"

### 5. Budget Analysis
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "How am I doing with my budget this month?",
    "personality": "to_the_point"
  }'
```
**Highlight**: "Agent analyzes spending by category and provides actionable recommendations"

## 🏗️ Project Structure

```
finance-agent-app/
├── backend/
│   ├── main.py                 # FastAPI app + endpoints
│   ├── router.py               # Intent classification
│   ├── context_builder.py      # Transaction summary builder
│   ├── agents/
│   │   ├── spending_agent.py   # Spending analysis
│   │   ├── budgeting_agent.py  # Budget recommendations
│   │   ├── investing_agent.py  # Investment advice
│   │   └── general_agent.py    # General queries
│   ├── models/
│   │   └── gemini_client.py    # Gemini API integration
│   ├── memory/
│   │   └── memory_manager.py   # User state management
│   └── personality/
│       └── tone_engine.py      # Personality + payday detection
├── transaction_data.json       # 500 synthetic transactions
└── README.md
```

## 🔧 Environment Variables

Create `backend/.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🎯 Hackathon Differentiators

1. **Context-Aware Reasoning** - Not just tracking, but understanding financial behavior
2. **Multi-Agent Architecture** - Specialized agents with unified state
3. **Dynamic Personality Engine** - Adaptive communication style
4. **Multimodal Input** - Receipt understanding via Gemini
5. **Data-Driven Advice** - Responses based on actual transaction patterns

## 📝 Testing

See `backend/TEST_COMMANDS.md` for detailed testing instructions.

## 🚧 Future Enhancements

- Live Plaid integration (currently using synthetic data)
- Web-based onboarding flow
- Dashboard visualization
- Missing expense detection
- ATM withdrawal reconciliation

## 👥 Team

- **Yukta** - System Architecture / Router
- **Monish** - Plaid Integration
- **Hemanth** - Agent Prompts
- **Deeksha** - Memory + Reconciliation
- **Anurag** - Flutter Frontend

## 📄 License

MIT
