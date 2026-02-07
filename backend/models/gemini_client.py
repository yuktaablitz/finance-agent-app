class GeminiClient:
    """
    Demo-only Gemini client.
    Returns a predictable response for hackathon stability.
    """

    def __init__(self):
        pass

    def generate(self, prompt: str) -> str:
        return f"Gemini response for:\n{prompt}"
