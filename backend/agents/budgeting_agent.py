from models.gemini_client import GeminiClient


class BudgetingAgent:

    def __init__(self):
        self.llm = GeminiClient()

    def run(self, message: str, context: dict):
        
        transaction_summary = context.get('transaction_summary', {})
        
        prompt = f"""
You are a budgeting specialist who helps people build sustainable financial plans. Your approach:
1. Assess current spending distribution across needs/wants/savings
2. Apply budgeting frameworks (50/30/20 rule, zero-based budgeting) to their situation
3. Calculate savings rate and compare to recommended benchmarks
4. Identify budget leaks (categories where spending exceeds typical ranges)
5. Create realistic category budgets based on their income and goals
6. Suggest reallocation strategies that don't feel restrictive

Communication Style: {context['tone']}
Style Notes: {context.get('tone_description', '')}

FINANCIAL DATA:"""
        
        if transaction_summary:
            prompt += f"""
- Current Balance: ${transaction_summary.get('estimated_balance', 0):,.2f}
- Total Spent: ${transaction_summary.get('total_spent', 0):,.2f}
- Total Income: ${transaction_summary.get('total_income', 0):,.2f}

SPENDING BY CATEGORY:"""
            for cat, amount in transaction_summary.get('spending_by_category', {}).items():
                prompt += f"\n- {cat}: ${amount:,.2f}"
        else:
            prompt += "\n(No transaction data available)"
        
        prompt += f"""

USER QUESTION: {message}

BUDGETING METHODOLOGY:
1. Calculate their current savings rate: (Income - Spending) / Income
2. Break down spending into: Essentials (housing, food, transport), Discretionary (dining, entertainment), Savings/Debt
3. Compare to 50/30/20 guideline (50% needs, 30% wants, 20% savings)
4. Identify top 3 categories for potential reduction
5. Propose specific dollar amounts for each category budget
6. Suggest one immediate action they can take this week
7. Set a realistic monthly savings target

Use their actual numbers. Be specific about which categories to adjust and by how much. Make it feel achievable."""

        # Use high thinking level for budget planning and analysis
        result = self.llm.generate(prompt, thinking_level="high")

        return {
            "response": result
        }
