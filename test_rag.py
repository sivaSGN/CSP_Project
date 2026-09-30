import sys
from retrieve import retrieve_with_schemes
from rag_chain import generate_answer

# Ensure Windows terminal outputs Unicode properly (e.g. ₹ symbol)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def run_rag_pipeline(question: str) -> str:
    """
    Complete end-to-end RAG workflow:
    1. Accept question.
    2. Retrieve top 3 chunks and source scheme names from FAISS vector_db.
    3. Send chunks + question + scheme names to Groq (openai/gpt-oss-20b).
    4. Print answer with source schemes.
    """
    print(f"\n[Step 1] Question: {question}")
    
    print("\n[Step 2] Retrieving top 3 chunks & scheme names from FAISS vector_db...")
    chunks, scheme_names = retrieve_with_schemes(question, top_k=3)
    
    print("\n" + "-" * 50)
    print(f"IDENTIFIED SOURCE SCHEMES ({len(scheme_names)}):")
    print("-" * 50)
    if scheme_names:
        for s in scheme_names:
            print(f"  • {s}")
    else:
        print("  (None identified)")

    print("\n" + "-" * 50)
    print(f"RETRIEVED CHUNKS ({len(chunks)}):")
    print("-" * 50)
    if chunks:
        for idx, chunk in enumerate(chunks, 1):
            print(f"\n--- [Chunk {idx}] ---")
            print(chunk)
    else:
        print("[No relevant chunks found]")
    print("-" * 50)
    
    print("\n[Step 3] Sending context & question to Groq (openai/gpt-oss-20b)...")
    answer = generate_answer(
        question=question,
        retrieved_context=chunks,
        scheme_names=scheme_names,
    )
    
    print("\n[Step 4] Final Answer & Source Schemes:")
    print("=" * 60)
    print(answer)
    print("=" * 60)
    
    return answer


if __name__ == "__main__":
    # Use CLI argument if provided, otherwise default test question
    test_question = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "What are the eligibility criteria and benefits for the PM-KISAN scheme?"
    )
    
    print("=" * 60)
    print("🌾 FARMERS WELFARE ASSISTANT - RAG PIPELINE TEST")
    print("=" * 60)
    
    run_rag_pipeline(test_question)
