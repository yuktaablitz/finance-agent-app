# Flutter App Setup & Testing Guide

## Prerequisites

### Install Flutter SDK
```bash
# Download Flutter SDK from https://flutter.dev/docs/get-started/install/macos
# Or use Homebrew:
brew install --cask flutter

# Verify installation
flutter doctor
```

## Quick Start

### 1. Navigate to Flutter App
```bash
cd /Users/blitz/Documents/finance-agent-app/frontend/flutter_app
```

### 2. Create .env File (Already Done ✅)
```bash
echo "API_BASE_URL=http://127.0.0.1:8000" > assets/.env
```

### 3. Install Dependencies
```bash
flutter pub get
```

### 4. Run the App

**Option A: iOS Simulator** (Recommended for Mac)
```bash
# Open iOS Simulator
open -a Simulator

# Run app
flutter run
```

**Option B: Chrome (Web)**
```bash
flutter run -d chrome
```

**Option C: Android Emulator**
```bash
# Start Android emulator first, then:
flutter run
```

## Testing the Full Stack

### Backend Status
✅ **Running on http://localhost:8000**
✅ **Gemini 3 Flash Preview** with thinking levels
✅ **478 transactions loaded** for demo_user_123
✅ **All endpoints working**

### What to Test in Flutter App

#### 1. Chat Interface
- Open the app
- You'll see a chat interface with personality selector
- Type: "Can I afford a $200 jacket?"
- Switch personalities and ask the same question
- Observe different response styles

#### 2. Personality Switching
Test all 5 personalities:
- **Zen Coach**: Calm, reflective
- **Tough Love**: Direct, challenging  
- **Supportive**: Encouraging
- **To The Point**: Brief, factual
- **No BS**: Blunt, data-driven

#### 3. Receipt Upload
- Tap the **receipt icon** (floating action button)
- Choose camera or gallery
- Upload a receipt image
- Gemini 3 will extract: merchant, amount, date, category
- Transaction gets added to your context

#### 4. Context-Aware Responses
After uploading receipts or loading transactions:
- Ask: "How much have I spent on food?"
- Ask: "Should I invest $500?"
- Ask: "Am I on track with my budget?"

Responses will reference your actual transaction data!

## Troubleshooting

### "Unable to connect to backend"
```bash
# Check backend is running
curl http://localhost:8000/

# Restart backend if needed
cd /Users/blitz/Documents/finance-agent-app/backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### "No transactions found"
```bash
# Reload transactions
curl -X POST "http://localhost:8000/load-transactions?user_id=demo_user_123"
```

### Flutter build errors
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter run
```

## Alternative: Test Backend Directly (No Flutter Needed)

If you can't install Flutter right now, test the full Gemini 3 capabilities via curl:

### Test Chat with Different Personalities
```bash
# Zen Coach
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Can I afford a $200 jacket?",
    "personality": "zen_coach"
  }'

# Tough Love
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Can I afford a $200 jacket?",
    "personality": "tough_love"
  }'

# Supportive
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Can I afford a $200 jacket?",
    "personality": "supportive"
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

### Test Investment Analysis
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_123",
    "message": "Should I invest $500 this month?",
    "personality": "no_bs"
  }'
```

## What's Working Right Now

✅ **Gemini 3 Flash Preview** - Latest model with advanced reasoning
✅ **Thinking Levels** - High for analysis, low for routing, medium for general
✅ **Context-Aware** - References actual transaction data in responses
✅ **Personality Engine** - 5 different communication styles
✅ **Transaction Loading** - 478 synthetic transactions loaded
✅ **Receipt Upload Endpoint** - Ready for multimodal processing
✅ **Media Resolution** - High-res OCR for receipts

## Demo Script (Without Flutter)

For your hackathon presentation, you can demo the backend capabilities:

1. **Show transaction loading**
2. **Test same question with different personalities** (show 3 responses)
3. **Show budget analysis** with specific numbers
4. **Show investment readiness assessment**
5. **Explain Flutter UI** (show screenshots or mockups)

The backend is fully functional with Gemini 3 - that's the core innovation!
