#!/bin/bash

echo "🚀 Testing Finance Agent API..."
echo ""

# Test 1: Health Check
echo "1. Health Check:"
curl -s http://localhost:8000/health | python -m json.tool
echo ""

# Test 2: Tough Love Personality
echo "2. Tough Love - Jacket Purchase:"
curl -X POST "http://localhost:8000/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I buy a $200 jacket?",
    "user_context": {
      "user_id": "test_user",
      "financial_personality": "tough_love",
      "payday_day": 15,
      "monthly_income": 5000.0,
      "current_balance": 1200.0,
      "monthly_budget": 4000.0
    }
  }' | python -m json.tool
echo ""

# Test 3: Supportive Personality - Investment
echo "3. Supportive - Investment Question:"
curl -X POST "http://localhost:8000/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I invest $1000?",
    "user_context": {
      "user_id": "test_user",
      "financial_personality": "supportive",
      "payday_day": 15,
      "monthly_income": 5000.0,
      "current_balance": 3000.0,
      "monthly_budget": 4000.0
    }
  }' | python -m json.tool
echo ""

# Test 4: No BS Personality - Coffee Subscription
echo "4. No BS - Coffee Subscription:"
curl -X POST "http://localhost:8000/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I buy this $50 coffee subscription?",
    "user_context": {
      "user_id": "test_user", 
      "financial_personality": "no_bs",
      "payday_day": 15,
      "monthly_income": 5000.0,
      "current_balance": 800.0,
      "monthly_budget": 4000.0
    }
  }' | python -m json.tool
echo ""

echo "✅ API Tests Complete!"
echo "📖 Visit http://localhost:8000/docs for interactive testing"
