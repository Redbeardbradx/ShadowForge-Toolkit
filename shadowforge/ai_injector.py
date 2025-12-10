from dotenv import load_dotenv
import os
import json
import requests

# Load keys from .env at runtime
load_dotenv()

class ShadowForgeAI:
    def __init__(self, persona_path="config/persona.json", api_key_env="GROK_API_KEY"):
        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError("Missing GROK_API_KEY environment variable.")
        
        with open(persona_path, "r") as f:
            self.persona = json.load(f)

    def ask(self, prompt):
        # BADBRAD mode check
        if prompt.startswith(self.persona["modes"]["badbrad_trigger"]):
            mode = "badbrad"
        else:
            mode = "default"

        payload = {
            "model": "grok-latest",
            "messages": [
                {"role": "system", "content": json.dumps(self.persona)},
                {"role": "user", "content": prompt}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        r = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
        return r.json()["choices"][0]["message"]["content"]
