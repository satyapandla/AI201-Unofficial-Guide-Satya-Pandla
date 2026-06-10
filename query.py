"""
query.py
Retrieval + grounded generation.
Import ask() from app.py or run directly: python query.py
"""

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

load_dotenv()

CHROMA_DIR  = "./chroma_db"
COLLECTION  = "unofficial_guide"
TOP_K       = 4
MODEL_NAME  = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful college student advisor for George Mason University.

Answer the user's question using ONLY the information provided in the documents below.
Do NOT use any knowledge from your training data.

Rules:
- If the documents contain enough information, give a clear, specific answer.
- Always end your response with a "Sources:" line listing the document names you drew from.
- If the documents do NOT contain enough information to answer the question, respond with exactly:
  "I don't have enough information in my documents to answer that question."
- Never make up facts, statistics, or advice not present in the documents."""

_model      = None
_collection = None
_groq       = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client      = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection(COLLECTION)
    return _collection


def _get_groq():
    global _groq
    if _groq is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set. Add it to your .env file.")
        _groq = Groq(api_key=api_key)
    return _groq


# ── Main functions ─────────────────────────────────────────────────────────────
def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """Return top-k chunks with text, source label, url, and distance."""
    model      = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings = query_embedding,
        n_results        = k,
        include          = ["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text":     doc,
            "source":   meta["source_label"],
            "url":      meta["source_url"],
            "distance": round(dist, 4),
        })

    return chunks


def generate(query: str, chunks: list[dict]) -> str:
    """Generate a grounded answer from retrieved chunks."""
    groq = _get_groq()

    # Format context block
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Document {i}: {chunk['source']}]\n{chunk['text']}"
        )
    context = "\n\n".join(context_parts)

    user_message = f"""Documents:
{context}

Question: {query}"""

    response = groq.chat.completions.create(
        model    = MODEL_NAME,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature = 0.2,   # low temp = more grounded, less creative
        max_tokens  = 600,
    )

    return response.choices[0].message.content.strip()


def ask(query: str) -> dict:
    """
    Full RAG pipeline: retrieve → generate.
    Returns:
        {
            "answer":  str,
            "sources": [{"source": str, "url": str, "distance": float}],
            "chunks":  [full chunk dicts]
        }
    """
    chunks  = retrieve(query)
    answer  = generate(query, chunks)
    sources = [{"source": c["source"], "url": c["url"], "distance": c["distance"]}
               for c in chunks]
    return {"answer": answer, "sources": sources, "chunks": chunks}


# ── CLI test mode ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_queries = [
        "What tips exist for registering for classes successfully?",
        "What career paths are common for college graduates?",
        "What advice do students get about succeeding in college?",
        "What dining or housing options exist at GMU?",
        "How can students find internships at GMU?",
    ]

    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        print('='*60)
        result = ask(q)

        print(f"\nANSWER:\n{result['answer']}")
        print(f"\nRETRIEVED CHUNKS ({len(result['chunks'])}):")
        for i, chunk in enumerate(result["chunks"], 1):
            print(f"  [{i}] {chunk['source']} (distance: {chunk['distance']})")
            print(f"      {chunk['text'][:100]}...")