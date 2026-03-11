import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMInterface:
    def __init__(self):
        # Loads key from .env automatically
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def ask_llm(self, prompt, system_message="You are a senior software architect."):
        """
        Sends code snippets or questions to Groq and gets a text response.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, # Low temperature for consistent, factual analysis
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"ML Error: {e}"