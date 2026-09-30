import os
import sys
from typing import List, Optional, Union
from dotenv import load_dotenv
from groq import Groq

# Configure UTF-8 encoding for console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Load environment variables from .env
load_dotenv()

# Default Groq model configuration
DEFAULT_MODEL = "openai/gpt-oss-20b"
FALLBACK_MESSAGE = "Information not available in the knowledge base."

# Global Groq client cache
_GROQ_CLIENT: Optional[Groq] = None


def get_groq_client() -> Groq:
    """Initialize and return the Groq client using GROQ_API_KEY from environment."""
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please set GROQ_API_KEY in your .env file."
            )
        _GROQ_CLIENT = Groq(api_key=api_key)
    return _GROQ_CLIENT


def generate_answer(
    question: str,
    retrieved_context: Union[str, List[str]],
    scheme_names: Optional[List[str]] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
) -> str:
    """
    Generate an answer strictly using the provided context, optionally listing source schemes.

    Args:
        question (str): The user's query/question.
        retrieved_context (str or list): Context text or list of chunk strings.
        scheme_names (list, optional): List of source scheme names.
        model (str): Groq model identifier (default: 'openai/gpt-oss-20b').
        temperature (float): Sampling temperature (0.0 for deterministic answers).

    Returns:
        str: Generated answer.
    """
    if not question or not question.strip():
        return "Please provide a valid question."

    # Convert list of chunks to a single string if needed
    if isinstance(retrieved_context, list):
        context_str = "\n\n---\n\n".join(c.strip() for c in retrieved_context if c.strip())
    else:
        context_str = retrieved_context.strip() if retrieved_context else ""

    # If no context was provided, return fallback
    if not context_str:
        return FALLBACK_MESSAGE

    client = get_groq_client()

    system_prompt = (
        "You are an agricultural welfare assistant.\n\n"
        "Answer ONLY using the provided context.\n\n"
        "If the answer is not found in the context, reply:\n"
        "'Information not available in the knowledge base.'"
    )

    user_prompt = f"Context:\n{context_str}\n\nQuestion:\n{question}"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        raw_answer = response.choices[0].message.content
        answer = raw_answer.strip() if raw_answer else FALLBACK_MESSAGE

        # If answer is found (not the fallback message) and scheme names are provided, append source schemes
        if answer != FALLBACK_MESSAGE and scheme_names:
            unique_schemes = [s for s in scheme_names if s]
            if unique_schemes:
                schemes_formatted = "\n".join(f"- {s}" for s in unique_schemes)
                answer = f"{answer}\n\n**Source Schemes:**\n{schemes_formatted}"

        return answer
    except Exception as e:
        return f"Error generating answer via Groq API ({model}): {str(e)}"


# Alias
run_rag_chain = generate_answer


if __name__ == "__main__":
    test_question = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "What are the eligibility criteria and benefits for the PM-KISAN scheme?"
    )

    try:
        from retrieve import retrieve_with_schemes
        chunks, schemes = retrieve_with_schemes(test_question, top_k=3)
    except Exception:
        chunks = [
            "Scheme Name: Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)\n"
            "Benefits: ₹6,000 per year through three equal DBT instalments."
        ]
        schemes = ["Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"]

    print(f"\nQUESTION: {test_question}")
    print(f"SCHEMES: {schemes}")
    print("-" * 50)
    
    result = generate_answer(test_question, retrieved_context=chunks, scheme_names=schemes)
    print("\nANSWER WITH SOURCE SCHEMES:")
    print("=" * 60)
    print(result)
    print("=" * 60)
