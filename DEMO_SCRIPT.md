# 🎬 AccountantAI - Hackathon Demo Script

## Pre-Demo Setup (5 minutes before)

```bash
# 1. Start backend
cd backend
export GEMINI_API_KEY=your_key
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Load transaction data
curl -X POST "http://localhost:8000/load-transactions?user_id=demo_user_123"
```

---

## Demo Flow (5-7 minutes)

### Opening (30 seconds)
"Hi, we're Team AccountantAI. We built an AI-powered personal finance assistant that doesn't just track your spending—it **understands** your financial behavior and gives you contextual advice."

### 1. The Problem (30 seconds)
"Apps like Mint and RocketMoney track transactions, but they don't **reason** about your financial decisions. We wanted to build something that acts like a real accountant—someone who knows your patterns, understands context, and adapts their communication style to what works for you."

### 2. Show the Architecture (45 seconds)
**[Show diagram or explain]**
- "We built a **multi-agent system** powered by Gemini"
- "Router agent classifies your intent"
- "Specialized agents (spending, budgeting, investing) handle specific domains"
- "Personality engine adapts the tone"
- "All agents share context from your actual transaction data"

### 3. Live Demo - Data Loading (30 seconds)
```bash
curl -X POST "http://localhost:8000/load-transactions?user_id=demo_user_123"
```

**Say**: "We've loaded 500 synthetic transactions. In production, this would come from Plaid. Notice the summary—total spent, income, top categories."

### 4. Live Demo - Context-Aware Chat (90 seconds)

**Query 1: Spending Decision**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Should I buy a $200 jacket?",
    "personality": "tough_love"
  }'
```

**Say**: "Notice how the agent references **actual data**—my spending on clothing, my current balance, recent transactions. This isn't generic advice—it's personalized."

**Query 2: Budget Analysis**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "How am I doing with my budget?",
    "personality": "supportive"
  }'
```

**Say**: "The budgeting agent analyzes spending by category and provides actionable recommendations based on my patterns."

### 5. Show Personality Switching (45 seconds)

**Same question, different personality:**
```bash
# Zen Coach
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Can I afford to eat out tonight?",
    "personality": "zen_coach"
  }'

# Tough Love
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Can I afford to eat out tonight?",
    "personality": "tough_love"
  }'
```

**Say**: "Same financial data, completely different communication style. Users can choose what motivates them."

### 6. Multimodal - Receipt Upload (45 seconds)
```bash
curl -X POST "http://localhost:8000/upload-receipt?user_id=demo_user_123" \
  -F "image=@sample_receipt.jpg"
```

**Say**: "Gemini's multimodal capabilities let us extract structured transaction data from receipt images. This captures cash spending that wouldn't show up in bank transactions."

### 7. Closing - Key Differentiators (30 seconds)

**"What makes this different?"**
1. **Context-aware reasoning** - Not just tracking, but understanding behavior
2. **Multi-agent architecture** - Specialized expertise with shared state
3. **Dynamic personality** - Adapts to what motivates you
4. **Multimodal input** - Receipt understanding via Gemini
5. **Data-driven advice** - Every response is grounded in your actual patterns

**"Thank you! Questions?"**

---

## Backup Demos (if time allows)

### Payday Effect Detection
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "I just got paid, should I treat myself?",
    "personality": "no_bs",
    "is_payday": true
  }'
```

### Investment Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Should I invest $500 this month?",
    "personality": "to_the_point"
  }'
```

---

## Anticipated Questions & Answers

**Q: How does this compare to existing apps?**
A: "Apps like Mint track transactions. We add reasoning—understanding *why* you spend, detecting patterns, and giving contextual advice. Plus, our personality engine adapts communication style."

**Q: What about privacy?**
A: "All data stays in memory during the demo. In production, we'd use encrypted storage and never share transaction data with third parties."

**Q: Is the Plaid integration working?**
A: "We have the Plaid sandbox integration built. For this demo, we're using 500 synthetic transactions to show the full capability without API rate limits."

**Q: How do you handle edge cases?**
A: "Our router agent has fallback logic. If intent classification is uncertain, we route to the general agent. We also have retry logic and error handling for API calls."

**Q: What's next?**
A: "Live Plaid integration, web dashboard, missing expense detection (reconciling ATM withdrawals with cash receipts), and mobile app deployment."

---

## Technical Highlights for Judges

- **Gemini Integration**: Text generation + multimodal (receipt understanding)
- **Agent Architecture**: Router + 4 specialized agents with shared context
- **Prompt Engineering**: Dynamic prompts with transaction summaries, category breakdowns, and personality modifiers
- **State Management**: In-memory user context with transaction history
- **API Design**: RESTful endpoints with clear contracts

---

## Troubleshooting

**If Gemini API fails:**
- "We're hitting rate limits. Let me show you a cached response..."
- Have a backup JSON response ready

**If demo runs slow:**
- "Gemini is processing the full transaction context. In production, we'd cache common queries."

**If something breaks:**
- "Let me show you the architecture diagram instead and walk through how it would work..."
- Always have backup slides/diagrams
