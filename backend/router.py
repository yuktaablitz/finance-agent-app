from agents.spending_agent import SpendingAgent
from agents.budgeting_agent import BudgetingAgent
from agents.investing_agent import InvestingAgent
from agents.general_agent import GeneralAgent
from models.gemini_client import GeminiClient
import json


class Router:

    def __init__(self):

        self.llm = GeminiClient()

        self.agents = {
            "spending": SpendingAgent(),
            "budgeting": BudgetingAgent(),
            "investing": InvestingAgent(),
            "general": GeneralAgent()
        }

    def classify_intent(self, message: str):

        prompt = f"""
You are an intent classification system.

Classify the user's financial query into ONE of:

- spending
- budgeting
- investing
- general

Return ONLY JSON like:

{{ "intent": "investing" }}

User message:
{message}
"""

        # Use low thinking level for fast intent classification
        result = self.llm.generate(prompt, thinking_level="low")

        try:
            parsed = json.loads(result)
            return parsed.get("intent", "general")
        except:
            return "general"

    def dispatch(self, message: str, context: dict):

        intent = self.classify_intent(message)

        agent = self.agents.get(intent, self.agents["general"])

        response = agent.run(message, context)

        return intent, response
