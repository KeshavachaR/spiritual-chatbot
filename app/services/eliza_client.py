# app/services/eliza_client.py

import os
import requests
from typing import List, Dict

ELIZA_URL = os.getenv("ELIZA_URL", "http://localhost:5101/reply")

def get_eliza_reply(message: str, history: List[Dict[str, str]] = None) -> str:
    try:
        resp = requests.post(
            ELIZA_URL,
            json={"message": message, "history": history or []},
            timeout=8,
        )
        if resp.status_code == 200:
            text = resp.json().get("text", "").strip()
            return text or "Okay."
    except requests.RequestException as e:
        print("ElizaOS error:", e)
    return "Sorry, I couldn’t respond just now."

