"""Cadena de consulta RAG (retrieval + LLM)."""

from __future__ import annotations

from dataclasses import dataclass

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config import LLM_BASE_URL, LLM_MODEL, TOP_K, read_api_key
from src.ingest import load_vectorstore
from src.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


@dataclass
class RAGResult:
    answer: str
    sources: list[str]
    documents: list[Document]


def get_llm(model: str | None = None) -> ChatOpenAI:
    api_key = read_api_key()
    if not api_key:
        raise ValueError(
            "Falta LLM_API_KEY. Revisa el archivo .env y reinicia Streamlit."
        )
    return ChatOpenAI(
        model=model or LLM_MODEL,
        api_key=api_key,
        base_url=LLM_BASE_URL,
        temperature=0.1,
    )


def format_context(documents: list[Document]) -> str:
    parts: list[str] = []
    for i, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "desconocido")
        tipo = doc.metadata.get("tipo", "otro")
        parts.append(
            f"[Fragmento {i} | fuente={source} | tipo={tipo}]\n{doc.page_content}"
        )
    return "\n\n".join(parts)


def extract_sources(documents: list[Document]) -> list[str]:
    seen: list[str] = []
    for doc in documents:
        source = doc.metadata.get("source", "desconocido")
        if source not in seen:
            seen.append(source)
    return seen


def ask(
    question: str,
    *,
    vectorstore: FAISS | None = None,
    top_k: int | None = None,
    model: str | None = None,
) -> RAGResult:
    store = vectorstore or load_vectorstore()
    k = top_k or TOP_K
    documents = store.similarity_search(question, k=k)
    context = format_context(documents)

    llm = get_llm(model=model)
    user_content = USER_PROMPT_TEMPLATE.format(
        context=context, question=question
    )
    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]
    )
    answer = (
        response.content
        if isinstance(response.content, str)
        else str(response.content)
    )
    return RAGResult(
        answer=answer.strip(),
        sources=extract_sources(documents),
        documents=documents,
    )
