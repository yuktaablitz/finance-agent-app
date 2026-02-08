from models.gemini_client import GeminiClient


class InvestingAgent:

    def __init__(self):
        self.llm = GeminiClient()

    def run(self, message: str, context: dict):
        
        transaction_summary = context.get('transaction_summary', {})
        
        prompt = f"""
You are an investment advisor focused on helping people build wealth responsibly. Your framework:
1. Assess investment readiness (emergency fund, high-interest debt, stable income)
2. Evaluate available capital for investing (surplus after expenses)
3. Discuss risk tolerance based on financial stability
4. Recommend investment vehicles appropriate for their situation (index funds, retirement accounts, etc.)
5. Explain dollar-cost averaging and long-term thinking
6. Address common investment mistakes (timing market, emotional decisions)

Communication Style: {context['tone']}
Style Notes: {context.get('tone_description', '')}

FINANCIAL POSITION:"""
        
        if transaction_summary:
            prompt += f"""
- Current Balance: ${transaction_summary.get('estimated_balance', 0):,.2f}
- Monthly Income: ${transaction_summary.get('total_income', 0):,.2f}
- Monthly Spending: ${transaction_summary.get('total_spent', 0):,.2f}
- Monthly Surplus: ${transaction_summary.get('total_income', 0) - transaction_summary.get('total_spent', 0):,.2f}

SPENDING CATEGORIES:"""
            for cat, amount in transaction_summary.get('spending_by_category', {}).items():
                prompt += f"\n- {cat}: ${amount:,.2f}"
        else:
            prompt += "\n(No financial data available)"
        
        prompt += f"""

USER QUESTION: {message}

INVESTMENT ASSESSMENT:
1. Check prerequisites: Do they have 3-6 months emergency fund? Any high-interest debt?
2. Calculate investable surplus: Income - Expenses - Emergency fund contribution
3. If surplus < $100/month: Focus on increasing income or reducing expenses first
4. If surplus $100-500/month: Recommend retirement account (401k/IRA) with index funds
5. If surplus > $500/month: Discuss diversified portfolio strategy
6. Emphasize: Investing is long-term (5+ years), don't invest money needed soon
7. Warn against: Individual stock picking, crypto speculation, timing the market

Be honest about whether now is the right time to invest. If they're not ready, explain what to fix first."""

        result = self.llm.generate(prompt)

        return {
            "response": result
        }
