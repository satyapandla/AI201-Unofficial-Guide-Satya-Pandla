
import gradio as gr
from query import ask

# ── Handler ────────────────────────────────────────────────────────────────────
def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", "", ""

    result  = ask(question)
    answer  = result["answer"]

  
    source_lines = []
    for s in result["sources"]:
        source_lines.append(f"• {s['source']}  (similarity distance: {s['distance']})")
    sources_text = "\n".join(source_lines)


    chunk_lines = []
    for i, chunk in enumerate(result["chunks"], 1):
        chunk_lines.append(
            f"[Chunk {i}] {chunk['source']} | distance: {chunk['distance']}\n"
            f"{chunk['text'][:300]}{'...' if len(chunk['text']) > 300 else ''}"
        )
    chunks_text = "\n\n".join(chunk_lines)

    return answer, sources_text, chunks_text


# ── UI ─────────────────────────────────────────────────────────────────────────
with gr.Blocks(title="GMU Patriot's Unofficial Guide") as demo:
    gr.Markdown(
        """
        # GMU Patriot's Unofficial Guide
        *A RAG system for college survival knowledge.*
        Ask anything about GMU campus life, registration, dining, parking, clubs, internships, or college success tips.
        Answers are grounded in real documents with every response including source attribution.
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            question_box = gr.Textbox(
                label       = "Your question",
                placeholder = "e.g. What tips exist for registering for classes?",
                lines       = 2,
            )
            ask_btn = gr.Button("Ask", variant="primary")

        with gr.Column(scale=3):
            answer_box = gr.Textbox(
                label = "Answer",
                lines = 8,
                interactive = False,
            )

    with gr.Accordion("Sources retrieved", open=True):
        sources_box = gr.Textbox(
            label       = "Documents used",
            lines       = 4,
            interactive = False,
        )

    with gr.Accordion("Retrieved chunks (for inspection)", open=False):
        chunks_box = gr.Textbox(
            label       = "Raw chunks returned by vector search",
            lines       = 12,
            interactive = False,
        )

    gr.Examples(
        examples=[
            ["What tips exist for registering for classes successfully?"],
            ["What career paths are common for college graduates?"],
            ["What advice do students get about succeeding in college?"],
            ["What dining or housing options exist at GMU?"],
            ["How can students find internships at GMU?"],
            ["What is the weather like on Mars?"],   # out-of-scope test
        ],
        inputs=question_box,
    )

    ask_btn.click(
        fn      = handle_query,
        inputs  = question_box,
        outputs = [answer_box, sources_box, chunks_box],
    )
    question_box.submit(
        fn      = handle_query,
        inputs  = question_box,
        outputs = [answer_box, sources_box, chunks_box],
    )

if __name__ == "__main__":
    demo.launch()