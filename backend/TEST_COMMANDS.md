# Backend Testing Commands

## 1. Start the Server

```bash
cd /Users/blitz/Documents/finance-agent-app/backend
export GEMINI_API_KEY=your_actual_key_here
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 2. Load Transaction Data

```bash
curl -X POST "http://localhost:8000/load-transactions?user_id=demo_user_123" \
  -H "Content-Type: application/json"
```

Expected response:
```json
{
  "status": "ok",
  "transactions_loaded": 500,
  "total_spent": 12345.67,
  "total_income": 8500.00,
  "top_categories": {...}
}
```

## 3. Test Chat with Transaction Context

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Should I buy a $200 jacket?",
    "personality": "tough_love"
  }'
```

Expected: Agent should reference your actual spending patterns and balance!

## 4. Test Different Queries

### Spending Analysis
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "How much have I spent on food this month?",
    "personality": "supportive"
  }'
```

### Budget Check
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Am I on track with my budget?",
    "personality": "zen_coach"
  }'
```

### General Financial Question
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "What should I focus on financially?",
    "personality": "to_the_point"
  }'
```

## 5. Verify Loaded Transactions

```bash
curl "http://localhost:8000/get-transactions/demo_user_123?limit=10"
```

## 6. Test Receipt Upload (with an image file)

```bash
curl -X POST "http://localhost:8000/upload-receipt?user_id=demo_user_123" \
  -F "image=@/path/to/receipt.jpg"
```

## Key Things to Verify

✅ Agents reference actual transaction data (categories, amounts, merchants)
✅ Tone changes based on personality selection
✅ Balance and spending totals are accurate
✅ Receipt upload extracts transaction details
✅ Chat responses are contextual and data-driven

## Troubleshooting

- **"Missing GEMINI_API_KEY"**: Set the environment variable before starting
- **"Transaction file not found"**: Check the path in `/load-transactions` endpoint
- **Empty responses**: Verify Gemini API key is valid and has quota
