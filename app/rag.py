# app/rag.py

from dataclasses import dataclass
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_ollama import ChatOllama

PERSIST_DIR = "app/chroma_bible"

def format_docs(docs):
    return "\n\n".join(d.page_content.strip() for d in docs)

# --- Unified Short-Reply Prompts ---
SYSTEM_PROMPT_SIMPLE = """You are a warm, friendly Christian companion.
Reply in short, natural sentences — like a real person talking.
Avoid long explanations. Use plain, everyday language.
If scripture is clearly requested, include one short verse only.
Never give more than two sentences plus one verse.
User goal: {goal}
Conversation so far:
{history}"""

SYSTEM_PROMPT_DEEP = """You are a compassionate Christian companion centered on Jesus and the Bible.
Keep replies short (1–2 sentences) and practical.
Use retrieved passages as the only biblical source; include at most one short verse already present in context.
If context is insufficient, ask one brief clarifying question.
Never exceed two sentences plus one verse.
User goal: {goal}
Conversation so far:
{history}"""

# --- Optional Router ---
def choose_mode(user_input: str) -> str:
    casual_keywords = [
        "hi", "hello", "how are you", "what's up", "motivate", "encourage",
        "good morning", "good evening", "how's it going"
    ]
    if any(word in user_input.lower() for word in casual_keywords):
        return "simple"
    return "deep"

@dataclass
class RAGConfig:
    backend: str = "ollama"
    model: str = "llama3"
    k: int = 5
    temperature: float = 0.7
    max_tokens: int = 60  # shorter replies

    def ask(self, instance, question: str, goal: str = "", history: str = "", style: str = "deep") -> str:
        question = question if isinstance(question, str) else str(question)
        goal = goal if isinstance(goal, str) else str(goal or "")
        history = history if isinstance(history, str) else str(history or "")

        if style == "simple":
            raw = instance.simple_chain.invoke({"question": question, "goal": goal, "history": history})
        else:
            raw = instance.deep_chain.invoke({"question": question, "goal": goal, "history": history})

        return raw if isinstance(raw, str) else str(raw)

class SpiritualRAG:
    def __init__(self, config: RAGConfig):
        self.config = config

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.retriever = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=embeddings
        ).as_retriever(search_kwargs={"k": config.k})

        self.llm = ChatOllama(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

        # --- Simple mode: no retrieval ---
        simple_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_SIMPLE),
            ("human", "{question}")
        ])

        # --- Deep mode: with retrieval ---
        deep_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_DEEP),
            ("system", "Context:\n{context}"),
            ("human", "{question}")
        ])

        # Input mapping for deep mode (retrieval)
        deep_input_map = RunnableParallel(
            context=(lambda x: x["question"]) | self.retriever | format_docs,
            question=RunnablePassthrough(),
            goal=RunnablePassthrough(),
            history=RunnablePassthrough(),
        )

        # Input mapping for simple mode (no retrieval)
        simple_input_map = RunnableParallel(
            question=RunnablePassthrough(),
            goal=RunnablePassthrough(),
            history=RunnablePassthrough(),
        )

        self.simple_chain = simple_input_map | simple_prompt | self.llm | StrOutputParser()
        self.deep_chain = deep_input_map | deep_prompt | self.llm | StrOutputParser()

    def ask(self, question: str, goal: str = "", history=None, style: str = None) -> str:
        history_text = history if isinstance(history, str) else str(history or "")
        # Auto-route if style not explicitly given
        if not style:
            style = choose_mode(question)
        return self.config.ask(self, question=question, goal=goal, history=history_text, style=style)

