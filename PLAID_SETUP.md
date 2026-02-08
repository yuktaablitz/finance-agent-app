# Plaid Integration Setup Guide

## Overview
This guide will help you set up real Plaid integration for AccountantAI to fetch live bank transactions.

## Prerequisites
1. Plaid account (sign up at https://dashboard.plaid.com/signup)
2. Backend server running
3. Python environment with dependencies installed

## Step 1: Get Plaid Credentials

1. **Sign up for Plaid**:
   - Go to https://dashboard.plaid.com/signup
   - Create a free account (Sandbox is free)

2. **Get your credentials**:
   - After signup, go to https://dashboard.plaid.com/team/keys
   - Copy your `client_id` and `sandbox` secret
   - You'll see something like:
     ```
     client_id: 5f8a9b2c3d4e5f6a7b8c9d0e
     sandbox: 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d
     ```

## Step 2: Configure Backend

1. **Update `.env` file**:
   ```bash
   cd /Users/blitz/Documents/finance-agent-app/backend
   nano .env
   ```

2. **Replace placeholder values**:
   ```
   GEMINI_API_KEY=AIzaSyBeETcCwn_nZPV72JximoHPaMeE4xjXHkE

   # Plaid API Configuration
   PLAID_CLIENT_ID=your_actual_client_id_here
   PLAID_SECRET=your_actual_sandbox_secret_here
   PLAID_ENV=sandbox
   ```

3. **Install Plaid Python library**:
   ```bash
   pip3 install plaid-python==16.0.0
   ```

## Step 3: Restart Backend

```bash
cd /Users/blitz/Documents/finance-agent-app/backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Step 4: Test Plaid Integration

1. **Open the web app**:
   ```bash
   open /Users/blitz/Documents/finance-agent-app/web/app.html
   ```

2. **Connect a bank**:
   - Go to "AI Accountant" tab
   - Click "Connect Bank" button
   - Plaid Link will open
   - Select any bank (in Sandbox mode)
   - Use test credentials:
     - Username: `user_good`
     - Password: `pass_good`

3. **Verify transactions**:
   - After connecting, transactions will be fetched automatically
   - Check "Transactions" tab to see live data
   - AI Accountant will now use real transaction data

## Plaid Sandbox Test Credentials

Plaid provides test credentials for different scenarios:

| Username | Password | Description |
|----------|----------|-------------|
| user_good | pass_good | Successful authentication |
| user_bad | pass_good | Invalid credentials |
| user_custom | pass_good | Custom test data |

## API Endpoints

### 1. Create Link Token
```bash
POST http://localhost:8000/plaid/create-link-token
{
  "user_id": "demo_user_123"
}
```

### 2. Exchange Public Token
```bash
POST http://localhost:8000/plaid/exchange-token
{
  "user_id": "demo_user_123",
  "public_token": "public-sandbox-..."
}
```

### 3. Fetch Transactions
```bash
POST http://localhost:8000/plaid/fetch-transactions
{
  "user_id": "demo_user_123"
}
```

## How It Works

1. **User clicks "Connect Bank"**:
   - Frontend requests link token from backend
   - Backend calls Plaid API to create link token

2. **Plaid Link opens**:
   - User selects their bank
   - Authenticates with credentials
   - Plaid returns public token

3. **Token exchange**:
   - Frontend sends public token to backend
   - Backend exchanges for access token
   - Access token stored in user memory

4. **Fetch transactions**:
   - Backend uses access token to fetch transactions
   - Transactions stored in user memory
   - AI agents now have access to real data

## Troubleshooting

### Error: "Missing PLAID_CLIENT_ID or PLAID_SECRET"
- Make sure you've updated `.env` with your actual Plaid credentials
- Restart the backend server after updating `.env`

### Error: "invalid_credentials"
- In Sandbox mode, use `user_good` / `pass_good`
- Check that PLAID_ENV is set to `sandbox` in `.env`

### Error: "Plaid Link not opening"
- Make sure backend is running on port 8000
- Check browser console for JavaScript errors
- Verify Plaid Link script is loaded (check network tab)

## Moving to Production

When ready to use real banks (not Sandbox):

1. **Apply for Production access** in Plaid Dashboard
2. **Update `.env`**:
   ```
   PLAID_ENV=production
   PLAID_SECRET=your_production_secret_here
   ```
3. **Restart backend**

## Resources

- Plaid Dashboard: https://dashboard.plaid.com
- Plaid Docs: https://plaid.com/docs/
- Plaid API Reference: https://plaid.com/docs/api/
- Sandbox Guide: https://plaid.com/docs/sandbox/
