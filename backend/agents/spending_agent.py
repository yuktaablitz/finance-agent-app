# agents/spending_agent.py

from models.gemini_client import GeminiClient


class SpendingAgent:

    def __init__(self):
        self.llm = GeminiClient()

    def run(self, message: str, context: dict):
        
        # Build enhanced prompt with transaction data
        transaction_summary = context.get('transaction_summary', {})
        
        prompt = f"""
You are a financial advisor specializing in spending behavior analysis. Your role is to:
1. Analyze spending patterns across categories and time periods
2. Calculate affordability based on current balance, income velocity, and committed expenses
3. Identify spending trends (increasing/decreasing categories, unusual transactions)
4. Provide actionable recommendations grounded in their actual financial data

Communication Style: {context['tone']}
Style Notes: {context.get('tone_description', '')}

CURRENT FINANCIAL SNAPSHOT:"""
        
        if transaction_summary:
            prompt += f"""
- Estimated Balance: ${transaction_summary.get('estimated_balance', 0):,.2f}
- Total Spent: ${transaction_summary.get('total_spent', 0):,.2f}
- Total Income: ${transaction_summary.get('total_income', 0):,.2f}
- Transaction Count: {transaction_summary.get('transaction_count', 0)}

TOP SPENDING CATEGORIES:"""
            for cat, amount in transaction_summary.get('spending_by_category', {}).items():
                prompt += f"\n- {cat}: ${amount:,.2f}"
            
            prompt += "\n\nRECENT TRANSACTIONS:"
            for tx in transaction_summary.get('recent_transactions', [])[:5]:
                prompt += f"\n- {tx['date']}: {tx['merchant']} - ${abs(tx['amount']):,.2f} ({tx['category']})"
        else:
            prompt += "\n(No transaction data loaded yet)"
        
        # Add payday context if available
        payday_effect = context.get('payday_effect')
        if payday_effect:
            prompt += f"\n\nPAYDAY ALERT: {payday_effect.get('warning_message', '')}"
        
        prompt += f"""

USER QUESTION: {message}

ANALYSIS FRAMEWORK:
1. Reference specific numbers from their transaction data above
2. Calculate spending velocity (daily/weekly burn rate) if relevant
3. Compare proposed spending against category averages
4. Consider balance adequacy for upcoming expenses
5. Identify any concerning patterns (overspending in categories, frequency of similar purchases)
6. Provide clear yes/no recommendation with reasoning
7. Suggest specific alternatives or adjustments if declining

Be conversational but precise. Cite actual transaction amounts and categories. Make your reasoning transparent."""

        # Use high thinking level for complex financial analysis
        result = self.llm.generate(prompt, thinking_level="high")
        
        return {
            "response": result
        }
