"""Ingesta de documentos PDF/CSV y construccion del indice FAISS."""

from __future__ import annotations

import shutil
from pathlib import Path

from langchain_community.document_loaders import CSVLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_RAW_DIR,
    EMBEDDING_MODEL,
    VECTORSTORE_DIR,
)

SOURCE_TYPE = {
    "politicas_cuenta.pdf": "politica",
    "tarifas_comisiones.pdf": "tarifa",
    "seguridad_fraude.pdf": "seguridad",
    "terminos_condiciones.pdf": "terminos",
    "tarifas.csv": "tarifa",
}


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_documents(raw_dir: Path | None = None) -> list[Document]:
    """Carga PDFs y CSV desde data/raw con metadata de fuente y tipo."""
    directory = raw_dir or DATA_RAW_DIR
    if not directory.exists():
        raise FileNotFoundError(
            f"No existe el directorio de datos: {directory}. "
            "Ejecuta primero: python scripts/generate_docs.py"
        )

    documents: list[Document] = []

    for pdf_path in sorted(directory.glob("*.pdf")):
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = pdf_path.name
            doc.metadata["tipo"] = SOURCE_TYPE.get(pdf_path.name, "otro")
        documents.extend(docs)

    for csv_path in sorted(directory.glob("*.csv")):
        loader = CSVLoader(file_path=str(csv_path), encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = csv_path.name
            doc.metadata["tipo"] = SOURCE_TYPE.get(csv_path.name, "otro")
        documents.extend(docs)

    if not documents:
        raise ValueError(f"No se encontraron documentos en {directory}")

    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def build_vectorstore(
    documents: list[Document] | None = None,
    persist: bool = True,
) -> FAISS:
    """Construye (y opcionalmente persiste) el indice FAISS."""
    docs = documents if documents is not None else load_documents()
    chunks = split_documents(docs)
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    if persist:
        VECTORSTORE_DIR.parent.mkdir(parents=True, exist_ok=True)
        if VECTORSTORE_DIR.exists():
            shutil.rmtree(VECTORSTORE_DIR)
        vectorstore.save_local(str(VECTORSTORE_DIR))

    return vectorstore


def load_vectorstore() -> FAISS:
    """Carga el indice FAISS existente o lo construye si no hay."""
    index_file = VECTORSTORE_DIR / "index.faiss"
    embeddings = get_embeddings()
    if index_file.exists():
        return FAISS.load_local(
            str(VECTORSTORE_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
    return build_vectorstore(persist=True)


def main() -> None:
    docs = load_documents()
    chunks = split_documents(docs)
    print(f"Documentos cargados: {len(docs)}")
    print(f"Chunks generados: {len(chunks)}")
    build_vectorstore(docs, persist=True)
    print(f"Indice FAISS guardado en: {VECTORSTORE_DIR}")


if __name__ == "__main__":
    main()
