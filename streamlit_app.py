# streamlit_app.py

import uuid
import json
import requests
import streamlit as st
from app.rag import SpiritualRAG, RAGConfig

st.set_page_config(page_title="🙏 Spiritual Chatbot", page_icon="📖", layout="centered")

def stringify_history(history, limit=10):
    if isinstance(history, str):
        return history
    if isinstance(history, list):
        lines = []
        for m in history[-limit:]:
            role = "User" if m.get("role") in ("human", "user") else "Assistant"
            content = m.get("content", "")
            if not isinstance(content, str):
                content = json.dumps(content, ensure_ascii=False)
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
    return str(history)

@st.cache_resource
def load_local_rag(model_name: str = "llama3", k: int = 5, temp: float = 0.7, max_tokens: int = 120):
    return SpiritualRAG(RAGConfig(model=model_name, k=k, temperature=temp, max_tokens=max_tokens))

# Sidebar
st.sidebar.title("Settings")
backend_mode = st.sidebar.radio("Backend mode", ["Local RAG", "FastAPI API"], index=0)
reply_style = st.sidebar.radio("Reply style", ["auto", "simple", "deep"], index=0)
goal = st.sidebar.text_input("Goal (optional)", value="")
with st.sidebar.expander("Local RAG config", expanded=(backend_mode == "Local RAG")):
    model_name = st.text_input("Ollama model", value="llama3")
    top_k = st.number_input("Retriever k", min_value=1, max_value=12, value=5, step=1)
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
    max_tokens = st.number_input("Max tokens", min_value=16, max_value=512, value=120, step=8)
with st.sidebar.expander("FastAPI config", expanded=(backend_mode == "FastAPI API")):
    api_url = st.text_input("POST /chat URL", value="http://127.0.0.1:8000/chat")
    st.caption("Run: uvicorn app.main:app --reload --port 8000")
col1, _ = st.sidebar.columns(2)
with col1:
    if st.button("Clear Chat"):
        st.session_state.history = []
        st.session_state.session_id = f"ui-{uuid.uuid4().hex[:12]}"
        st.rerun()

# Session state
if "history" not in st.session_state:
    st.session_state.history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"ui-{uuid.uuid4().hex[:12]}"

# Main UI
st.title("🙏 Spiritual Chatbot")
st.write("Short, warm replies grounded in scripture when helpful.")

# Show history
for m in st.session_state.history:
    role = "You" if m["role"] == "human" else "Bot"
    st.markdown(f"**{role}:** {m['content']}")

# Input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message:")
    submitted = st.form_submit_button("Send")

def call_api(message: str, history, mode: str, goal: str):
    payload = {
        "message": message,
        "history": [{"role": "user" if h["role"] == "human" else "assistant", "content": h["content"]} for h in history],
        "mode": mode,
        "goal": goal,
        "session_id": st.session_state.session_id,
    }
    r = requests.post(api_url, json=payload, timeout=180)
    r.raise_for_status()
    return r.json().get("reply", "")

if submitted and user_input.strip():
    # Append user message
    st.session_state.history.append({"role": "human", "content": user_input})
    history_text = stringify_history(st.session_state.history)

    with st.spinner("Thinking..."):
        try:
            if backend_mode == "Local RAG":
                # Auto: keyword route
                def spiritual_intent(t: str) -> bool:
                    kws = ["verse", "bible", "scripture", "jesus", "pray", "psalm", "proverb", "romans", "corinthians"]
                    tl = t.lower()
                    return any(k in tl for k in kws)
                mode = reply_style
                if reply_style == "auto":
                    mode = "deep" if spiritual_intent(user_input) else "simple"
                # For Local mode, both styles use the same RAG with different prompts
                answer = load_local_rag(model_name, int(top_k), temperature, int(max_tokens)) \
                    .ask(question=user_input, goal=goal, history=history_text, style=mode)
            else:
                answer = call_api(user_input, st.session_state.history, reply_style, goal)
        except Exception as e:
            answer = f"Something went wrong: {e}"

    # Append bot reply
    st.session_state.history.append({"role": "ai", "content": answer})
    st.rerun()

