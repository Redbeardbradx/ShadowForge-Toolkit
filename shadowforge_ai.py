import os
import json
import requests
from dotenv import load_dotenv


class ShadowForgeAI:
    def __init__(self, persona_path="config/persona.json", api_key_env="GROK_API_KEY"):
        # Load .env file
        load_dotenv()

        # Load API key
        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError("❌ Missing GROK_API_KEY in .env file.")

        # Load persona JSON
        if not os.path.exists(persona_path):
            raise FileNotFoundError(f"❌ persona.json not found at: {persona_path}")

        with open(persona_path, "r") as f:
            self.persona = json.load(f)

        # Pre-cache mode rules
        self.default_instr = self.persona["system_instructions"]["default"]
        self.badbrad_instr = self.persona["system_instructions"]["badbrad"]
        self.badbrad_trigger = self.persona["modes"]["badbrad_trigger"]

    def ask(self, prompt: str) -> str:
        # Detect BADBRAD mode
        if prompt.startswith(self.badbrad_trigger):
            system_msg = self.badbrad_instr
        else:
            system_msg = self.default_instr

        payload = {
            "model": "grok-small",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                json=payload,
                headers=headers
            )
        except Exception as e:
            return f"❌ Network/Request Error: {e}"

        if response.status_code != 200:
            return f"❌ API Error {response.status_code}: {response.text}"

        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            return f"❌ Bad API JSON Response: {response.text}"
