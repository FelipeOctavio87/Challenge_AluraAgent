"""Interfaz Streamlit del asistente NeoBank Alura."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
load_dotenv(ENV_PATH, override=True)

# Streamlit cachea imports: forzar recarga de src.* desde disco
for mod_name in list(sys.modules):
    if mod_name == "src" or mod_name.startswith("src."):
        del sys.modules[mod_name]

import streamlit as st

import src.config as config

importlib.reload(config)

from src.config import LLM_MODEL, TOP_K, VECTORSTORE_DIR, read_api_key
from src.ingest import build_vectorstore, load_vectorstore
from src.rag_chain import ask

SUGGESTED_QUESTIONS = [
    "Cual es la comision por transferencia SPEI saliente?",
    "Como activo el 2FA en NeoBank Alura?",
    "Cuales son los limites de transferencia SPEI diarios?",
    "Que hago si sospecho robo de credenciales?",
    "Cuanto cuesta la reposicion de tarjeta debit?",
]


def _load_api_key() -> str:
    load_dotenv(ENV_PATH, override=True)
    key = os.getenv("LLM_API_KEY", "").strip()
    if key:
        return key
    try:
        return read_api_key()
    except Exception:  # noqa: BLE001
        pass
    if not ENV_PATH.exists():
        return ""
    for line in ENV_PATH.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line.startswith("LLM_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _ensure_index() -> None:
    index_file = VECTORSTORE_DIR / "index.faiss"
    if not index_file.exists():
        with st.spinner("Construyendo indice FAISS por primera vez..."):
            build_vectorstore(persist=True)


def main() -> None:
    st.set_page_config(
        page_title="NeoBank Alura - Asistente RAG",
        page_icon=":bank:",
        layout="centered",
    )

    api_key = _load_api_key()

    st.title("Asistente NeoBank Alura")
    st.caption(
        "Consulta politicas, tarifas y seguridad del banco digital "
        "usando un agente RAG local (LangChain + FAISS)."
    )

    with st.sidebar:
        st.header("Configuracion")
        st.caption(f".env: `{ENV_PATH}`")
        st.caption(f"Existe: {ENV_PATH.exists()} | Key cargada: {bool(api_key)}")
        model = st.text_input("Modelo LLM", value=LLM_MODEL)
        top_k = st.slider("Top-K retrieval", min_value=1, max_value=8, value=TOP_K)
        st.info(
            "El asistente responde solo con documentos internos "
            "(PDF/CSV en data/raw). No inventa politicas."
        )
        if st.button("Reconstruir indice", use_container_width=True):
            with st.spinner("Reindexando documentos..."):
                build_vectorstore(persist=True)
            st.session_state.pop("vectorstore", None)
            st.success("Indice reconstruido.")

        st.subheader("Preguntas sugeridas")
        for q in SUGGESTED_QUESTIONS:
            if st.button(q, key=f"sug_{q}", use_container_width=True):
                st.session_state["pending_question"] = q

    if not api_key:
        st.error(
            "No se encontro LLM_API_KEY.\n\n"
            f"Ruta buscada: `{ENV_PATH}`\n"
            f"Existe el archivo: {ENV_PATH.exists()}\n\n"
            "Abre `.env`, verifica `LLM_API_KEY=gsk_...`, "
            "luego Ctrl+C y `streamlit run app.py`."
        )
        st.stop()

    _ensure_index()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption("Fuentes: " + ", ".join(message["sources"]))

    pending = st.session_state.pop("pending_question", None)
    prompt = st.chat_input("Escribe tu consulta sobre politicas NeoBank...")
    question = pending or prompt

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Consultando politicas..."):
                try:
                    if "vectorstore" not in st.session_state:
                        st.session_state.vectorstore = load_vectorstore()
                    result = ask(
                        question,
                        vectorstore=st.session_state.vectorstore,
                        top_k=top_k,
                        model=model,
                    )
                    st.markdown(result.answer)
                    if result.sources:
                        st.caption("Fuentes: " + ", ".join(result.sources))
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": result.answer,
                            "sources": result.sources,
                        }
                    )
                except Exception as exc:  # noqa: BLE001
                    error_msg = f"Error al consultar el agente: {exc}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_msg,
                            "sources": [],
                        }
                    )


if __name__ == "__main__":
    main()
