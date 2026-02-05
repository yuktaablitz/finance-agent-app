from models.gemini_client import GeminiClient


class GeneralAgent:

    def __init__(self):
        self.llm = GeminiClient()

    def run(self, message: str, context: dict):

        prompt = f"""
        You are a financial assistant.

        Tone: {context['tone']}
        Context: {context['memory']}

        User: {message}
        """

        result = self.llm.generate(prompt)

        return {
            "response": result
        }
