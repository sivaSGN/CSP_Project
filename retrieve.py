import sys
from pathlib import Path
from typing import List, Tuple, Optional
import warnings

# Configure UTF-8 encoding for console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Suppress minor deprecation warnings for clean execution
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Vector DB & Embedding configuration
VECTOR_DB_PATH = Path(__file__).parent / "vector_db"
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"

# Global vector store cache to avoid reloading on every call
_VECTOR_STORE: Optional[FAISS] = None


def get_vector_store() -> FAISS:
    """Load and cache the FAISS vector database with multilingual-e5-base embeddings."""
    global _VECTOR_STORE
    if _VECTOR_STORE is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        _VECTOR_STORE = FAISS.load_local(
            folder_path=str(VECTOR_DB_PATH),
            embeddings=embeddings,
            allow_dangerous_deserialization=True,
        )
    return _VECTOR_STORE


def retrieve_with_schemes(question: str, top_k: int = 3) -> Tuple[List[str], List[str]]:
    """
    Retrieve the top-k relevant document chunks and their associated scheme names.

    Args:
        question (str): The user query/question.
        top_k (int): Number of chunks to retrieve (default: 3).

    Returns:
        Tuple[List[str], List[str]]:
            - List of chunk texts (str)
            - List of unique source scheme names (str)
    """
    if not question or not question.strip():
        return [], []

    vector_store = get_vector_store()
    
    # Retrieve documents
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    docs = retriever.invoke(question)

    chunks = []
    scheme_names = []

    for doc in docs:
        content = doc.page_content.strip()
        chunks.append(content)

        # Extract scheme name from metadata if present
        scheme = doc.metadata.get("scheme_name") if hasattr(doc, "metadata") and doc.metadata else None
        
        # Fallback: extract from "Scheme Name: ..." in content if metadata is missing
        if not scheme:
            for line in content.splitlines():
                if line.lower().startswith("scheme name:"):
                    scheme = line.split(":", 1)[1].strip()
                    break

        if scheme and scheme not in scheme_names:
            scheme_names.append(scheme)

    return chunks, scheme_names


def retrieve_context(question: str) -> Tuple[str, List[str]]:
    """
    Retrieve combined context text and associated scheme names.

    Args:
        question (str): The user query or question.

    Returns:
        Tuple[str, List[str]]:
            - Concatenated text of top retrieved chunks.
            - List of unique scheme names.
    """
    chunks, scheme_names = retrieve_with_schemes(question, top_k=3)
    context_text = "\n\n---\n\n".join(chunks)
    return context_text, scheme_names


if __name__ == "__main__":
    test_question = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "What are the eligibility criteria and benefits for the PM-KISAN scheme?"
    )

    print(f"\n[Question]: {test_question}\n")
    print("=" * 60)
    print("RETRIEVING CHUNKS & SCHEME NAMES...")
    print("=" * 60)

    chunks, schemes = retrieve_with_schemes(test_question, top_k=3)

    print(f"\n📌 SOURCE SCHEMES ({len(schemes)}):")
    for s in schemes:
        print(f"  • {s}")

    print(f"\n📄 RETRIEVED CHUNKS ({len(chunks)}):")
    for idx, c in enumerate(chunks, 1):
        print(f"\n--- Chunk {idx} ---")
        print(c)

    print("\n" + "=" * 60)
