from models.gemini_client import GeminiClient


class InvestingAgent:

    def __init__(self):
        self.llm = GeminiClient()

    def run(self, message: str, context: dict):

        prompt = f"""
        You are an investing assistant.

        Tone: {context['tone']}
        Context: {context['memory']}

        User: {message}
        """

        result = self.llm.generate(prompt)

        return {
            "response": result
        }
