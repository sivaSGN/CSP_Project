import os
import sys
from pathlib import Path
from typing import List, Optional
import warnings

# Suppress minor deprecation warnings for cleaner CLI output
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# Default configuration
DEFAULT_VECTOR_DB_DIR = Path(__file__).parent / "vector_db"
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"

# Global cache for loaded vector store & embeddings to optimize repeat calls
_VECTOR_STORE = None


def get_embeddings(model_name: str = EMBEDDING_MODEL_NAME) -> HuggingFaceEmbeddings:
    """Initialize and return the HuggingFaceEmbeddings instance."""
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def load_vector_store(
    vector_db_path: Optional[str | Path] = None,
    embeddings: Optional[HuggingFaceEmbeddings] = None,
) -> FAISS:
    """
    Load the FAISS vector database from local directory.
    Uses allow_dangerous_deserialization=True required by modern LangChain for local pickle indexes.
    """
    global _VECTOR_STORE
    if _VECTOR_STORE is not None:
        return _VECTOR_STORE

    target_path = Path(vector_db_path) if vector_db_path else DEFAULT_VECTOR_DB_DIR

    if not target_path.exists():
        raise FileNotFoundError(
            f"Vector database directory not found at '{target_path}'. "
            "Please ensure 'index.faiss' and 'index.pkl' exist in the specified directory."
        )

    if embeddings is None:
        embeddings = get_embeddings()

    _VECTOR_STORE = FAISS.load_local(
        folder_path=str(target_path),
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )
    return _VECTOR_STORE


def retrieve_relevant_chunks(
    question: str,
    top_k: int = 3,
    vector_db_path: Optional[str | Path] = None,
) -> List[str]:
    """
    Accepts a question, performs similarity search on the FAISS vector store,
    and returns a list containing the text of the top-k relevant chunks.

    Args:
        question: User query / question string.
        top_k: Number of relevant chunks to retrieve (default: 3).
        vector_db_path: Optional path to vector database directory.

    Returns:
        List of strings containing the page_content of each retrieved chunk.
    """
    if not question or not question.strip():
        return []

    vector_store = load_vector_store(vector_db_path=vector_db_path)

    # Use modern LangChain retriever with Runnable interface (retriever.invoke)
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    docs = retriever.invoke(question)

    # Return chunk texts
    chunk_texts = [doc.page_content for doc in docs]
    return chunk_texts


if __name__ == "__main__":
    # Test query from command line argument or default example
    query = sys.argv[1] if len(sys.argv) > 1 else "What are the eligibility criteria and benefits for PM-KISAN scheme?"
    
    print(f"\n[Query]: {query}")
    print("Loading vector store & retrieving top 3 chunks...\n" + "=" * 60)
    
    results = retrieve_relevant_chunks(query, top_k=3)
    
    if not results:
        print("No relevant chunks found.")
    else:
        for idx, text in enumerate(results, 1):
            print(f"\n--- [Chunk {idx}] ---")
            print(text.strip())
        print("\n" + "=" * 60)
        print(f"Successfully retrieved {len(results)} chunk(s).")
