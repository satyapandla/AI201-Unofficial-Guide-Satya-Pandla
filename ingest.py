
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import chromadb

# ── Sources ────────────────────────────────────────────────────────────────────
SOURCES = [
    {"id": "doc_01", "url": "https://stories.marquette.edu/what-piece-of-advice-would-you-give-to-your-freshman-self-fc84d53af190", "label": "Marquette Freshman Advice"},
    {"id": "doc_02", "url": "https://www.southmountaincc.edu/current-students/top-tips-college-success",                          "label": "SMCC College Success Tips"},
    {"id": "doc_03", "url": "https://www.csun.edu/current-students/register/tips",                                                  "label": "CSUN Registration Tips"},
    {"id": "doc_04", "url": "https://www.gmu.edu/student-life/living-and-dining",                                                   "label": "GMU Dining & Living"},
    {"id": "doc_05", "url": "https://transportation.gmu.edu/parking/",                                                              "label": "GMU Parking"},
    {"id": "doc_06", "url": "https://si.gmu.edu/rso/",                                                                              "label": "GMU Clubs & Organizations"},
    {"id": "doc_07", "url": "https://catalog.gmu.edu/colleges-schools/engineering-computing/school-computing/information-sciences-technology/information-technology-bs/", "label": "GMU IT Degree"},
    {"id": "doc_08", "url": "https://www.gmu.edu/student-life",                                                                     "label": "GMU Student Life"},
    {"id": "doc_09", "url": "https://careers.gmu.edu/find-job-or-internship",                                                       "label": "GMU Internships & Careers"},
    {"id": "doc_10", "url": "https://www.bls.gov/careeroutlook/2021/article/field-of-degree-and-careers.htm",                       "label": "BLS Careers & College Majors"},
]

CHUNK_SIZE    = 800   # characters
CHUNK_OVERLAP = 50    # characters
CHROMA_DIR    = "./chroma_db"
COLLECTION    = "unofficial_guide"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; UnofficalGuideBot/1.0)"}


# ── Scraping ───────────────────────────────────────────────────────────────────
def fetch_text(url: str) -> str:
    """Fetch URL and return cleaned plain text."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [WARN] Could not fetch {url}: {e}")
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

   
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "form", "noscript", "iframe", "button",
                     "meta", "link"]):
        tag.decompose()

    
    raw = soup.get_text(separator="\n")
    return raw


def clean_text(raw: str) -> str:
    """Normalise whitespace and strip HTML entities / noise."""
    raw = raw.replace("&amp;", "&").replace("&nbsp;", " ") \
             .replace("&#39;", "'").replace("&quot;", '"')

    lines = [ln.strip() for ln in raw.splitlines()]

  
    noise_phrases = [
        "skip to", "sign in", "sign up", "open in app", "sitemap",
        "medium logo", "write", "search", "cookie", "navigation",
        "toggle", "menu", "footer", "back to top", "share",
        "read more", "click here", "©", "all rights reserved",
        "privacy policy", "terms of service", "follow us",
    ]

    filtered = []
    for ln in lines:
        lower = ln.lower()
        if any(phrase in lower for phrase in noise_phrases):
            continue
        if len(ln) < 20:  
            continue
        filtered.append(ln)

    raw = "\n".join(filtered)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw


# ── Chunking ───────────────────────────────────────────────────────────────────
def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Paragraph-aware chunker:
    1. Split on blank lines (paragraph boundaries).
    2. If a paragraph fits within `size`, keep it whole.
    3. If a paragraph exceeds `size`, slide a window with `overlap`.
    Returns only non-empty chunks.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    chunks = []

    for para in paragraphs:
        if len(para) <= size:
            chunks.append(para)
        else:
            start = 0
            while start < len(para):
                end = start + size
                chunks.append(para[start:end])
                start += size - overlap

    return [c for c in chunks if len(c) > 30]  

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=== Unofficial Guide — Ingestion Pipeline ===\n")

    # Load embedding model
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Set up ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_DIR)


    try:
        client.delete_collection(COLLECTION)
        print("Deleted existing collection.\n")
    except Exception:
        pass

    collection = client.create_collection(COLLECTION)

    all_chunks   = []
    all_ids      = []
    all_embeddings = []
    all_metadatas  = []

    chunk_counter = 0

    for source in SOURCES:
        print(f"[{source['id']}] Fetching: {source['label']}")
        raw   = fetch_text(source["url"])
        if not raw:
            print("  → Skipped (no content)\n")
            continue

        clean = clean_text(raw)
        chunks = chunk_text(clean)

        print(f"  → {len(chunks)} chunks")

        if chunks:
            preview = chunks[0][:120].replace("\n", " ")
            print(f"  → Preview: \"{preview}…\"")

        for i, chunk in enumerate(chunks):
            cid = f"{source['id']}_chunk_{i:04d}"
            all_chunks.append(chunk)
            all_ids.append(cid)
            all_metadatas.append({
                "source_id":  source["id"],
                "source_label": source["label"],
                "source_url": source["url"],
                "chunk_index": i,
            })
            chunk_counter += 1

        time.sleep(0.5)  
        print()


    print(f"Embedding {chunk_counter} chunks...")
    all_embeddings = model.encode(all_chunks, show_progress_bar=True).tolist()

    print("Storing in ChromaDB...")
    BATCH = 500
    for i in range(0, len(all_chunks), BATCH):
        collection.add(
            ids        = all_ids[i:i+BATCH],
            documents  = all_chunks[i:i+BATCH],
            embeddings = all_embeddings[i:i+BATCH],
            metadatas  = all_metadatas[i:i+BATCH],
        )

    print(f"\n✅ Done. {chunk_counter} chunks stored in ChromaDB.")
    print(f"   Collection: '{COLLECTION}' at {CHROMA_DIR}/")

    # ── Chunk inspection: print 5 samples ─────────────────────────────────────
    print("\n── 5 Sample Chunks ──────────────────────────────────────────────────")
    results = collection.get(limit=5, include=["documents", "metadatas"])
    for doc, meta in zip(results["documents"], results["metadatas"]):
        print(f"\nSource : {meta['source_label']}")
        print(f"Chunk  : {doc[:300]}")
        print("-" * 60)

    print(f"\nTotal chunks recorded: {chunk_counter}")
    print("Update your README 'Final chunk count' with this number.")


if __name__ == "__main__":
    main()