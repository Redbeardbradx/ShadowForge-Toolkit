from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("GROK_API_KEY")
print("Loaded key:", key)
