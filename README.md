# Spiritual Chatbot Companion

A modular, scripture-grounded AI companion built with FastAPI, LangChain, Streamlit, and ElizaOS. Designed to feel genuinely human and supportive, this bot blends emotional warmth with technical precision — inspired by platforms like DSCPL Chat.

## Features

- Dual-mode routing: ElizaOS handles tone/emotion, FastAPI manages logic and RAG responses
- Scripture-based replies: Hybrid prompt engineering for brevity, clarity, and spiritual depth
- Devotional planner: Generates daily plans with progress tracking
- Plug-and-play architecture: Modular services for easy debugging and scaling
- Streamlit UI: Lightweight frontend for testing and interaction

## Quickstart

1. Clone the repo
   git clone https://github.com/KeshavachaR/spiritual-chatbot.git
   cd spiritual-chatbot

2. Install dependencies
   # Python backend
   pip install -r requirements.txt

   # Node service (ElizaOS)
   cd eliza_service
   npm install

3. Run services
   # Start ElizaOS
   cd eliza_service
   npm start

   # Start FastAPI backend
   uvicorn app.main:app --reload

   # Launch Streamlit frontend
   streamlit run app/ui.py

## Architecture Overview

[User Input]
     ↓
[Streamlit UI] → [FastAPI Backend] → [LangChain RAG]
     ↓                             ↘
[ElizaOS Node Service] ← [Tone + Emotion Routing]

## Project Structure

app/             → FastAPI backend and LangChain logic  
eliza_service/   → Node.js tone/emotion routing service  
prompts/         → Hybrid prompt templates  
chroma_bible/    → Chroma vector store for scripture embeddings  
.streamlit/      → Frontend config  

## Dev Philosophy

- Maintainable, modular code
- Emotionally resonant replies
- Token-safe hybrid prompts
- Benchmarking against DSCPL Chat

## Contributing

Pull requests welcome! If you're passionate about spiritual AI, prompt design, or modular architectures, feel free to fork and improve. Let’s build companions that uplift and support.

## License

MIT — open source, open heart.
