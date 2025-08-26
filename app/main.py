# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Dict
from app.rag import SpiritualRAG, RAGConfig
from app.services.eliza_client import get_eliza_reply

app = FastAPI(title="Spiritual Chatbot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

SESSIONS: Dict[str, List[Dict[str, str]]] = {}

rag = SpiritualRAG(RAGConfig(model="llama3", k=5, temperature=0.7, max_tokens=120))

class Msg(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Msg] = []
    mode: Literal["auto", "simple", "deep"] = "auto"
    goal: str | None = None
    session_id: str | None = None

def is_spiritual_intent(text: str) -> bool:
    keywords = ["verse", "bible", "scripture", "jesus", "pray", "psalm", "proverb", "romans", "corinthians"]
    return any(k in text.lower() for k in keywords)

def fallback_reply() -> str:
    return "I'm here for you. Let's take a small step together."

def handle_simple(message: str, history: List[Dict[str, str]]) -> str:
    reply = get_eliza_reply(message, history)
    return reply or fallback_reply()

def handle_deep(message: str, history: List[Dict[str, str]], goal: str) -> str:
    history_str = "\n".join(f"{m['role'].title()}: {m['content']}" for m in history[-10:])
    reply = rag.ask(question=message, goal=goal or "", history=history_str, style="deep")
    return reply or fallback_reply()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    user_history = [m.model_dump() for m in req.history]
    if req.session_id:
        user_history = SESSIONS.get(req.session_id, user_history)

    mode = req.mode
    if mode == "auto":
        mode = "deep" if is_spiritual_intent(req.message) else "simple"

    if mode == "simple":
        reply = handle_simple(req.message, user_history)
        route = "eliza"
    else:
        reply = handle_deep(req.message, user_history, req.goal or "")
        route = "rag"

    if req.session_id:
        sess = SESSIONS.get(req.session_id, [])
        sess.append({"role": "user", "content": req.message})
        sess.append({"role": "assistant", "content": reply})
        SESSIONS[req.session_id] = sess

    return {"reply": reply, "mode": mode, "route": route}

