# 🚀 Full Stack Setup - AccountantAI with Gemini 2.0

## ✨ Gemini 2.0 Flash Experimental Capabilities Showcased

This project demonstrates **Gemini 2.0 Flash Experimental** (latest model) capabilities:

1. **Advanced Financial Reasoning** - Multi-step analysis with 50/30/20 budgeting framework
2. **Context-Aware Decision Making** - Analyzes 478 transactions to provide personalized advice
3. **Multimodal Understanding** - Extracts structured data from receipt images
4. **Dynamic Personality Adaptation** - Same data, 5 different communication styles
5. **Spending Velocity Calculations** - Real-time burn rate and affordability analysis

---

## 🎯 Quick Start (5 Minutes)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip3 install fastapi uvicorn google-generativeai python-dotenv python-multipart --break-system-packages

# Set Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Start server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Server will start on http://localhost:8000**

### 2. Load Transaction Data (New Terminal)

```bash
curl -X POST "http://localhost:8000/load-transactions?user_id=demo_user_123"
```

Expected output:
```json
{
  "status": "ok",
  "transactions_loaded": 478,
  "total_spent": 39741.88,
  "total_income": 42500.0,
  "top_categories": {
    "Transfer": 19810.0,
    "Food and Drink": 8885.13,
    "Service": 4544.28,
    "Travel": 3237.25,
    "Shops": 2798.22
  }
}
```

### 3. Flutter App Setup (New Terminal)

```bash
cd frontend/flutter_app

# Create .env file
echo "API_BASE_URL=http://127.0.0.1:8000" > assets/.env

# Get dependencies
flutter pub get

# Run app (iOS Simulator / Android Emulator / Chrome)
flutter run
```

---

## 🎬 Demo Flow for Judges

### Part 1: Context-Aware Financial Reasoning (2 min)

**Show Gemini 2.0's analytical capabilities:**

1. **In Flutter app**, ask: *"Can I afford to spend $200 on a jacket?"*
2. **Switch personality** to "Tough Love"
3. **Agent response will reference**:
   - Your actual balance ($2,758.12)
   - Total spending ($39,741.88)
   - Specific spending patterns
   - Data-driven recommendation

**Key Point**: "Notice how Gemini 2.0 doesn't just say yes/no - it analyzes spending velocity, category trends, and provides reasoning."

### Part 2: Personality Engine (1 min)

**Show dynamic communication adaptation:**

1. Ask the **same question** with different personalities:
   - **Zen Coach**: Calm, reflective, long-term thinking
   - **Tough Love**: Direct, challenging, accountability-focused
   - **Supportive**: Encouraging, educational, confidence-building

**Key Point**: "Same financial data, same Gemini 2.0 model, but the personality engine adapts the communication style to what motivates each user."

### Part 3: Multimodal Receipt Understanding (2 min)

**Show Gemini 2.0's vision capabilities:**

1. Tap the **receipt icon** (floating action button)
2. Upload a receipt image (camera or gallery)
3. Tap **"Process Receipt"**
4. **Gemini 2.0 extracts**:
   - Merchant name
   - Amount
   - Date
   - Category
   - Description

**Key Point**: "Gemini 2.0's multimodal capabilities let us capture cash spending that wouldn't show up in bank transactions - critical for complete financial tracking."

### Part 4: Advanced Budget Analysis (1 min)

**Show structured financial planning:**

1. Ask: *"How am I doing with my budget this month?"*
2. **Gemini 2.0 provides**:
   - Savings rate calculation
   - 50/30/20 rule analysis
   - Category-specific recommendations
   - Actionable next steps

**Key Point**: "The agent applies professional budgeting frameworks to your actual data - this is financial advisor-level reasoning."

---

## 🧠 Gemini 2.0 Prompt Engineering

### Spending Agent Prompt Structure

```
You are a financial advisor specializing in spending behavior analysis. Your role is to:
1. Analyze spending patterns across categories and time periods
2. Calculate affordability based on current balance, income velocity, and committed expenses
3. Identify spending trends (increasing/decreasing categories, unusual transactions)
4. Provide actionable recommendations grounded in their actual financial data

CURRENT FINANCIAL SNAPSHOT:
- Estimated Balance: $2,758.12
- Total Spent: $39,741.88
- Total Income: $42,500.00
- Transaction Count: 478

TOP SPENDING CATEGORIES:
- Transfer: $19,810.00
- Food and Drink: $8,885.13
...

RECENT TRANSACTIONS:
- 2025-10-31: Domino's Pizza - $38.50 (Fast Food)
- 2025-10-31: Uber - $45.20 (Taxi)
...

USER QUESTION: Should I buy a $200 jacket?

ANALYSIS FRAMEWORK:
1. Reference specific numbers from their transaction data above
2. Calculate spending velocity (daily/weekly burn rate) if relevant
3. Compare proposed spending against category averages
4. Consider balance adequacy for upcoming expenses
5. Identify any concerning patterns
6. Provide clear yes/no recommendation with reasoning
7. Suggest specific alternatives or adjustments if declining
```

**Why This Works**:
- Structured reasoning framework guides Gemini 2.0
- Real transaction data provides grounding
- Specific output requirements ensure actionable advice
- Not verbose - focused on effectiveness

---

## 📊 Architecture Highlights

### Multi-Agent System
```
User Query → Router (Gemini 2.0 intent classification)
    ↓
┌─────────────┬──────────────┬──────────────┬──────────────┐
│  Spending   │  Budgeting   │  Investing   │   General    │
│   Agent     │    Agent     │    Agent     │    Agent     │
└─────────────┴──────────────┴──────────────┴──────────────┘
    ↓
Personality Engine (tone adaptation)
    ↓
Gemini 2.0 Flash Experimental
    ↓
Context-aware response with reasoning
```

### Key Differentiators

1. **Not just tracking** - Reasoning about financial behavior
2. **Not generic advice** - Grounded in actual transaction patterns
3. **Not one-size-fits-all** - Dynamic personality adaptation
4. **Not text-only** - Multimodal receipt understanding
5. **Not black box** - Transparent reasoning process

---

## 🔧 API Endpoints

### POST /chat
```json
{
  "user_id": "demo_user_123",
  "message": "Can I afford to eat out tonight?",
  "personality": "tough_love"
}
```

Response includes:
- `agent_used`: Which specialist handled the query
- `response`: Gemini 2.0 generated advice
- `tone`: Applied personality
- `tone_description`: Personality context

### POST /upload-receipt
```bash
curl -X POST "http://localhost:8000/upload-receipt?user_id=demo_user_123" \
  -F "image=@receipt.jpg"
```

Returns extracted transaction with Gemini 2.0 vision analysis.

### POST /load-transactions
```bash
curl -X POST "http://localhost:8000/load-transactions?user_id=demo_user_123"
```

Loads 478 synthetic transactions for demo.

---

## 🎯 What Makes This Gemini 2.0 Showcase

### 1. Advanced Reasoning
- **Not**: "You have $2,758, so yes you can afford $200"
- **Gemini 2.0**: "You've spent $39,741 this period. Your Food & Drink category is $8,885 (22% of spending). A $200 jacket would be 7% of your remaining balance. Given your spending velocity of $X/day, this leaves you with Y days of runway. Consider..."

### 2. Structured Analysis
- Applies 50/30/20 budgeting framework
- Calculates savings rate
- Identifies budget leaks
- Provides category-specific targets

### 3. Multimodal Integration
- Receipt image → Structured JSON
- Handles various receipt formats
- Extracts merchant, amount, date, category
- Integrates with transaction context

### 4. Personality Adaptation
- Same reasoning, different delivery
- Maintains consistency within personality
- Adapts to user preferences
- Increases engagement and follow-through

---

## 🚨 Important Notes

### Memory is In-Memory
- Transactions reset on server restart
- **Solution**: Re-run `/load-transactions` after restart
- For production: Add database persistence

### Model Configuration
- Using `gemini-2.0-flash-exp` (latest experimental)
- This is the cutting-edge Gemini model
- Shows latest capabilities for hackathon

### Flutter Platform Support
- iOS: Requires Xcode
- Android: Requires Android Studio
- Web: Works in Chrome (no image picker on web)
- **Recommendation**: Use iOS Simulator or Android Emulator for full demo

---

## 📝 Testing Commands

### Test Context-Aware Chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Should I invest $500 this month?",
    "personality": "zen_coach"
  }'
```

### Test Budget Analysis
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Create a budget plan for me",
    "personality": "to_the_point"
  }'
```

### Verify Transactions Loaded
```bash
curl "http://localhost:8000/get-transactions/demo_user_123?limit=5"
```

---

## 🎓 Talking Points for Judges

1. **"We're using Gemini 2.0 Flash Experimental"** - Latest model, cutting-edge capabilities

2. **"This isn't just transaction tracking"** - It's financial reasoning with context-aware analysis

3. **"The prompts are engineered for effectiveness"** - Structured frameworks, not verbose instructions

4. **"Multimodal capabilities are key"** - Cash transactions via receipt images complete the picture

5. **"Personality engine increases engagement"** - Same data, communication style that works for each user

6. **"This is production-ready architecture"** - Multi-agent system, proper separation of concerns

---

## 🏆 Success Metrics

✅ **478 transactions** loaded and analyzed
✅ **5 personality styles** working dynamically
✅ **Multimodal receipt processing** with Gemini 2.0 vision
✅ **Context-aware responses** referencing actual data
✅ **Professional financial frameworks** (50/30/20, savings rate, etc.)
✅ **Full-stack integration** Flutter ↔ FastAPI ↔ Gemini 2.0

**You're ready to demo! 🚀**
