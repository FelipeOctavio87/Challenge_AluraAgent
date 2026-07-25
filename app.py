"""Interfaz Streamlit del asistente NeoBank Alura."""

from __future__ import annotations

import html
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

from src.config import DATA_RAW_DIR, LLM_MODEL, TOP_K, VECTORSTORE_DIR, read_api_key
from src.ingest import build_vectorstore, load_vectorstore
from src.rag_chain import ask

SUGGESTED_QUESTIONS = [
    "Cual es la comision por transferencia SPEI saliente?",
    "Como activo el 2FA en NeoBank Alura?",
    "Cuales son los limites de transferencia SPEI diarios?",
    "Que hago si sospecho robo de credenciales?",
    "Cuanto cuesta la reposicion de tarjeta debit?",
]

CUSTOM_CSS = """
<style>
:root {
  --nb-bg: #F4F7FB;
  --nb-primary: #0B1F3A;
  --nb-accent: #2F6FED;
  --nb-surface: #FFFFFF;
  --nb-border: #D7E0EC;
  --nb-success: #12B76A;
  --nb-danger: #F04438;
  --nb-muted: #5B6B7C;
}

.stApp {
  background: var(--nb-bg);
}

[data-testid="stSidebar"] {
  background: var(--nb-surface);
  border-right: 1px solid var(--nb-border);
}

[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
  color: var(--nb-primary);
}

.nb-header {
  background: linear-gradient(135deg, #0B1F3A 0%, #143A66 55%, #1E4F8C 100%);
  color: #FFFFFF;
  border-radius: 18px;
  padding: 1.4rem 1.6rem;
  margin-bottom: 1.2rem;
  box-shadow: 0 10px 28px rgba(11, 31, 58, 0.18);
}

.nb-brand {
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0.85;
  margin-bottom: 0.35rem;
}

.nb-title {
  font-size: 1.85rem;
  font-weight: 700;
  margin: 0 0 0.75rem 0;
  line-height: 1.2;
}

.nb-badge {
  display: inline-block;
  background: rgba(47, 111, 237, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.28);
  color: #EAF2FF;
  border-radius: 999px;
  padding: 0.35rem 0.85rem;
  font-size: 0.85rem;
}

.nb-card {
  background: var(--nb-surface);
  border: 1px solid var(--nb-border);
  border-radius: 16px;
  padding: 1rem 1.1rem;
  margin-bottom: 1rem;
  box-shadow: 0 6px 18px rgba(11, 31, 58, 0.06);
}

.nb-section-title {
  color: var(--nb-primary);
  font-weight: 700;
  font-size: 1.05rem;
  margin: 0 0 0.75rem 0;
}

.nb-status {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.45rem 0;
  color: var(--nb-primary);
  font-size: 0.95rem;
}

.nb-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.nb-dot-ok { background: var(--nb-success); box-shadow: 0 0 0 3px rgba(18, 183, 106, 0.2); }
.nb-dot-bad { background: var(--nb-danger); box-shadow: 0 0 0 3px rgba(240, 68, 56, 0.18); }

.nb-answer {
  background: var(--nb-surface);
  border: 1px solid var(--nb-border);
  border-left: 4px solid var(--nb-accent);
  border-radius: 14px;
  padding: 0.95rem 1.05rem;
  box-shadow: 0 4px 14px rgba(11, 31, 58, 0.06);
  color: var(--nb-primary);
  line-height: 1.55;
}

.nb-doc-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.45rem 0;
  border-bottom: 1px solid var(--nb-border);
  color: var(--nb-primary);
  font-size: 0.92rem;
}

.nb-doc-row:last-child { border-bottom: none; }
.nb-doc-meta { color: var(--nb-muted); white-space: nowrap; }

div[data-testid="stChatMessage"] {
  background: transparent;
}

.stButton > button {
  border-radius: 12px !important;
  border: 1px solid var(--nb-border) !important;
  background: var(--nb-surface) !important;
  color: var(--nb-primary) !important;
  box-shadow: 0 2px 8px rgba(11, 31, 58, 0.05);
  transition: all 0.15s ease;
}

.stButton > button:hover {
  border-color: var(--nb-accent) !important;
  color: var(--nb-accent) !important;
  background: #EEF4FF !important;
}

button[kind="primary"] {
  background: var(--nb-accent) !important;
  color: #FFFFFF !important;
  border-color: var(--nb-accent) !important;
}

button[kind="primary"]:hover {
  background: #245AD1 !important;
  color: #FFFFFF !important;
}
</style>
"""


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
    try:
        lines = ENV_PATH.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return ""
    for line in lines:
        line = line.strip()
        if line.startswith("LLM_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _ensure_index() -> None:
    index_file = VECTORSTORE_DIR / "index.faiss"
    if not index_file.exists():
        with st.spinner("Construyendo indice FAISS por primera vez..."):
            build_vectorstore(persist=True)


def _faiss_ready() -> bool:
    return (VECTORSTORE_DIR / "index.faiss").exists()


def _list_raw_documents() -> list[tuple[str, str]]:
    if not DATA_RAW_DIR.exists():
        return []
    docs: list[tuple[str, str]] = []
    for path in sorted(DATA_RAW_DIR.iterdir()):
        if path.suffix.lower() in {".pdf", ".csv"} and path.is_file():
            size_kb = path.stat().st_size / 1024
            docs.append((path.name, f"{size_kb:.1f} KB"))
    return docs


def _status_row(label: str, ok: bool, detail: str) -> str:
    cls = "nb-dot-ok" if ok else "nb-dot-bad"
    state = "Activo" if ok else "Inactivo"
    safe_label = html.escape(label)
    safe_detail = html.escape(detail)
    return (
        f'<div class="nb-status">'
        f'<span class="nb-dot {cls}"></span>'
        f"<strong>{safe_label}</strong> — {state} "
        f'<span style="color:var(--nb-muted)">({safe_detail})</span>'
        f"</div>"
    )


def _render_assistant_message(content: str, sources: list[str] | None = None) -> None:
    safe = html.escape(content).replace("\n", "<br>")
    st.markdown(f'<div class="nb-answer">{safe}</div>', unsafe_allow_html=True)
    if sources:
        with st.expander("Ver fuentes consultadas"):
            for source in sources:
                st.markdown(f"- `{source}`")


def _render_header() -> None:
    st.markdown(
        """
        <div class="nb-header">
          <div class="nb-brand">NeoBank Alura</div>
          <h1 class="nb-title">Asistente NeoBank Alura</h1>
          <span class="nb-badge">Agente de IA para Consultas Internas - NeoBank Alura</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_suggested_questions() -> None:
    st.markdown('<div class="nb-card">', unsafe_allow_html=True)
    st.markdown(
        '<p class="nb-section-title">Preguntas sugeridas</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, question in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 2]:
            if st.button(question, key=f"sug_main_{i}", use_container_width=True):
                st.session_state["pending_question"] = question
    st.markdown("</div>", unsafe_allow_html=True)


def _render_documents_panel() -> None:
    docs = _list_raw_documents()
    with st.expander("Documentos cargados (data/raw)", expanded=False):
        if not docs:
            st.caption("No hay PDF/CSV en data/raw. Ejecuta scripts/generate_docs.py.")
            return
        rows = []
        for name, size in docs:
            rows.append(
                f'<div class="nb-doc-row">'
                f"<span>{html.escape(name)}</span>"
                f'<span class="nb-doc-meta">{html.escape(size)}</span>'
                f"</div>"
            )
        st.markdown(
            f'<div class="nb-card" style="margin:0">{"".join(rows)}</div>',
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="NeoBank Alura - Asistente RAG",
        page_icon=":bank:",
        layout="wide",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    api_key = _load_api_key()
    _render_header()

    if not api_key:
        with st.sidebar:
            st.markdown("### Estado del Sistema")
            st.markdown(
                _status_row("FAISS", _faiss_ready(), "indice vectorial local")
                + _status_row("Groq API", False, "sin LLM_API_KEY"),
                unsafe_allow_html=True,
            )
        st.error(
            "No se encontro LLM_API_KEY.\n\n"
            f"Ruta buscada: `{ENV_PATH}`\n"
            f"Existe el archivo: {ENV_PATH.exists()}\n\n"
            "Abre `.env`, verifica `LLM_API_KEY=gsk_...`, "
            "luego Ctrl+C y `streamlit run app.py`."
        )
        st.stop()

    _ensure_index()

    with st.sidebar:
        st.markdown("### Controles")
        model = st.text_input("Modelo LLM", value=LLM_MODEL)
        top_k = st.slider("Top-K retrieval", min_value=1, max_value=8, value=TOP_K)
        st.caption(
            "El asistente responde solo con documentos internos "
            "(PDF/CSV en data/raw)."
        )
        if st.button(
            "Reconstruir indice",
            use_container_width=True,
            type="primary",
        ):
            with st.spinner("Reindexando documentos..."):
                build_vectorstore(persist=True)
            st.session_state.pop("vectorstore", None)
            st.success("Indice reconstruido.")

        st.divider()
        st.markdown("### Estado del Sistema")
        st.markdown(
            _status_row("FAISS", _faiss_ready(), "indice vectorial local")
            + _status_row("Groq API", True, "LLM conectado"),
            unsafe_allow_html=True,
        )

    _render_suggested_questions()
    _render_documents_panel()

    st.markdown('<div class="nb-card">', unsafe_allow_html=True)
    st.markdown(
        '<p class="nb-section-title">Consulta al agente</p>',
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                _render_assistant_message(
                    message["content"], message.get("sources") or []
                )
            else:
                st.markdown(message["content"])

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
                    _render_assistant_message(result.answer, result.sources)
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

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
