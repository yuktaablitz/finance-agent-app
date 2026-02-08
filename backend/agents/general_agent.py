from models.gemini_client import GeminiClient


class GeneralAgent:

    def __init__(self):
        self.llm = GeminiClient()

    def run(self, message: str, context: dict):
        
        transaction_summary = context.get('transaction_summary', {})
        
        prompt = f"""
You are a helpful financial assistant.

TONE: {context['tone']}
Tone Description: {context.get('tone_description', '')}
"""
        
        if transaction_summary:
            prompt += f"\nUser's Financial Snapshot: Balance ${transaction_summary.get('estimated_balance', 0):,.2f}, Spent ${transaction_summary.get('total_spent', 0):,.2f}"
        
        prompt += f"\n\nUSER QUESTION: {message}"
        prompt += "\n\nProvide helpful financial guidance."

        result = self.llm.generate(prompt)

        return {
            "response": result
        }
