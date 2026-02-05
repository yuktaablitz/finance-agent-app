# router.py

from agents.spending_agent import SpendingAgent
from agents.budgeting_agent import BudgetingAgent
from agents.investing_agent import InvestingAgent
from agents.general_agent import GeneralAgent


class Router:

    def __init__(self):
        self.agents = {
            "spending": SpendingAgent(),
            "budgeting": BudgetingAgent(),
            "investing": InvestingAgent(),
            "general": GeneralAgent()
        }

    def classify_intent(self, message: str) -> str:
        """
        Simple starter intent classification.
        Replace later with LLM classifier.
        """

        msg = message.lower()

        if "spend" in msg or "expense" in msg:
            return "spending"
        elif "budget" in msg:
            return "budgeting"
        elif "invest" in msg or "stock" in msg:
            return "investing"
        else:
            return "general"

    def dispatch(self, message: str, context: dict):
        intent = self.classify_intent(message)

        agent = self.agents[intent]

        response = agent.run(message, context)

        return intent, response
