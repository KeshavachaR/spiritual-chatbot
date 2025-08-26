# Spiritual Chatbot Companion

A modular, warm, and scripture-grounded AI companion built with FastAPI, Streamlit, LangChain, and ElizaOS. Inspired by platforms like DSCPL Chat, this bot offers dual-mode routing, tone control, devotional plan generation, and progress tracking — all in a maintainable plug-and-play architecture.

---

## Features

- **Dual-mode routing**: ElizaOS handles emotional tone, FastAPI routes logic and RAG responses
- **Scripture-grounded replies**: Hybrid prompt engineering for warmth and brevity
- **Devotional planner**: Generates daily plans with progress tracking
- **Modular backend**: Drop-in services for easy debugging and scaling
- **Streamlit frontend**: Lightweight UI for testing and interaction

---

## Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/KeshavachaR/spiritual-chatbot.git
cd spiritual-chatbot

### INSTALL DEPENDENCIES

# Python backend
pip install -r requirements.txt

# Node service (ElizaOS)
cd eliza_service
npm install