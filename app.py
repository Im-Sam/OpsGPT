import gradio as gr
import logging
import os
import shutil
from pathlib import Path

from rag.ingestor import ingest_directory
from rag.embedder import build_vectorstore, add_documents
from rag.chain import build_chain, query

logging.basicConfig(level=logging.INFO)

DOCS_DIR = "data/docs"
DEMO_DIR = "demo_data"
os.makedirs(DOCS_DIR, exist_ok=True)

vectorstore = None
chain = None

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Root & Body ─────────────────────────────── */
:root {
    --bg:        #0b0d12;
    --surface:   #12151e;
    --surface2:  #1a1f2e;
    --border:    rgba(255,255,255,0.07);
    --accent:    #00e5a0;
    --accent2:   #0099ff;
    --danger:    #ff5c5c;
    --text:      #e4e8f0;
    --muted:     #6b7585;
    --mono:      'JetBrains Mono', monospace;
    --sans:      'DM Sans', sans-serif;
    --display:   'Syne', sans-serif;
}

body, .gradio-container {
    background: var(--bg) !important;
    font-family: var(--sans) !important;
    color: var(--text) !important;
}

.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ── Hide Gradio footer & header clutter ─────── */
footer, .built-with { display: none !important; }
.share-button { display: none !important; }

/* ── Main layout wrapper ─────────────────────── */
.main-wrap {
    display: flex;
    height: 100vh;
    overflow: hidden;
    background: var(--bg);
}

/* ── Sidebar ─────────────────────────────────── */
.sidebar-col {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
    min-width: 280px !important;
    max-width: 280px !important;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.sidebar-col .wrap {
    padding: 24px 20px !important;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

/* ── Logo / Header ───────────────────────────── */
#logo-md {
    border-bottom: 1px solid var(--border);
    padding-bottom: 20px;
    margin-bottom: 0;
}

#logo-md p {
    font-family: var(--display) !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    color: var(--text) !important;
    margin: 0 !important;
    letter-spacing: -0.5px;
}

#logo-md p span {
    color: var(--accent);
}

#logo-sub p {
    font-family: var(--mono) !important;
    font-size: 10px !important;
    color: var(--muted) !important;
    letter-spacing: 0.08em !important;
    margin: 0 !important;
    text-transform: uppercase;
}

/* ── Section labels ──────────────────────────── */
.section-label p {
    font-family: var(--mono) !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin: 0 0 8px !important;
}

/* ── Buttons ─────────────────────────────────── */
button.primary {
    background: var(--accent) !important;
    color: #051a0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
    transition: opacity 0.2s, transform 0.1s !important;
    cursor: pointer !important;
}

button.primary:hover { opacity: 0.85 !important; }
button.primary:active { transform: scale(0.97) !important; }

button.secondary {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
    padding: 10px 16px !important;
    transition: border-color 0.2s !important;
}

button.secondary:hover { border-color: var(--accent) !important; }

/* ── Status / Textboxes ──────────────────────── */
.gr-textbox textarea, .gr-textbox input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 11px !important;
    padding: 10px 12px !important;
    resize: none !important;
}

.gr-textbox label span {
    font-family: var(--mono) !important;
    font-size: 10px !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── File upload ─────────────────────────────── */
.gr-file {
    background: var(--surface2) !important;
    border: 1px dashed rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    transition: border-color 0.2s !important;
}

.gr-file:hover { border-color: var(--accent) !important; }

/* ── Chat column ─────────────────────────────── */
.chat-col {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    background: var(--bg) !important;
    overflow: hidden !important;
    padding: 0 !important;
}

/* ── Chat header bar ─────────────────────────── */
#chat-header {
    border-bottom: 1px solid var(--border);
    padding: 16px 24px;
    background: var(--surface);
}

#chat-header p {
    margin: 0;
    font-family: var(--mono) !important;
    font-size: 11px !important;
    color: var(--muted) !important;
}

/* ── ChatInterface wrapper ───────────────────── */
.chat-col > div { flex: 1; display: flex; flex-direction: column; }

/* ── Chatbot messages ────────────────────────── */
.message-wrap {
    padding: 20px 24px !important;
    gap: 16px !important;
    background: var(--bg) !important;
}

/* User bubble */
.message.user {
    background: var(--accent) !important;
    color: #051a0f !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 12px 16px !important;
    font-family: var(--sans) !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    max-width: 70% !important;
    margin-left: auto !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(0,229,160,0.15) !important;
}

/* Bot bubble */
.message.bot {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border-radius: 16px 16px 16px 4px !important;
    padding: 14px 18px !important;
    font-family: var(--sans) !important;
    font-size: 13.5px !important;
    line-height: 1.7 !important;
    max-width: 80% !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
}

.message.bot strong { color: var(--accent) !important; font-weight: 500 !important; }
.message.bot code {
    font-family: var(--mono) !important;
    font-size: 12px !important;
    background: rgba(255,255,255,0.07) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}

.message.bot ol, .message.bot ul {
    margin: 8px 0 8px 20px !important;
}

.message.bot li { margin: 5px 0 !important; }

/* Avatar icons */
.message.user .avatar-container { display: none !important; }
.message.bot .avatar-container img { display: none !important; }

/* ── Input row ───────────────────────────────── */
.input-row {
    padding: 16px 24px !important;
    background: var(--surface) !important;
    border-top: 1px solid var(--border) !important;
}

.input-row textarea {
    background: var(--surface2) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 13.5px !important;
    padding: 12px 16px !important;
    resize: none !important;
    transition: border-color 0.2s !important;
}

.input-row textarea:focus {
    border-color: rgba(0,229,160,0.4) !important;
    outline: none !important;
}

.input-row textarea::placeholder { color: var(--muted) !important; }

/* Send button */
#component-submit-btn, button[aria-label="Submit"] {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #051a0f !important;
    width: 40px !important;
    height: 40px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: opacity 0.2s !important;
}

/* ── Example pills ───────────────────────────── */
.examples-holder {
    padding: 12px 24px !important;
    background: var(--bg) !important;
    border-top: 1px solid var(--border) !important;
}

.examples-holder table td button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-family: var(--sans) !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
    transition: all 0.2s !important;
    white-space: nowrap !important;
}

.examples-holder table td button:hover {
    border-color: var(--accent) !important;
    color: var(--text) !important;
    background: rgba(0,229,160,0.08) !important;
}

/* ── Scrollbar ───────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ── Pulse animation for status dot ─────────── */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
    animation: pulse 2s ease-in-out infinite;
    margin-right: 6px;
}
"""

def initialize_with_demo():
    global vectorstore, chain
    try:
        chunks = ingest_directory(DEMO_DIR)
        vectorstore = build_vectorstore(chunks)
        chain = build_chain(vectorstore)
        return f"● Loaded {len(chunks)} chunks across 4 documents\n✓ Vector index built\n✓ Llama 3 chain ready"
    except Exception as e:
        return f"✗ Error: {e}"

def upload_and_ingest(files):
    global vectorstore, chain
    if not files:
        return "No files provided."
    upload_dir = Path(DOCS_DIR) / "uploads"
    upload_dir.mkdir(exist_ok=True)
    uploaded = []
    for file in files:
        dest = upload_dir / Path(file.name).name
        shutil.copy(file.name, dest)
        uploaded.append(dest.name)
    try:
        chunks = ingest_directory(str(upload_dir))
        vectorstore = add_documents(chunks, vectorstore)
        chain = build_chain(vectorstore)
        return f"✓ Ingested {len(uploaded)} file(s)\n✓ Index updated\n● {', '.join(uploaded)}"
    except Exception as e:
        return f"✗ Error: {e}"

def chat(message, history):
    global chain
    if chain is None:
        return "⚠ No documents loaded. Click Load Demo Data in the left panel first."
    try:
        result = query(chain, message)
        answer = result["answer"]
        citations = result["citations"]
        if citations:
            cite_block = "\n\n---\n📎 Sources\n"
            for i, c in enumerate(citations, 1):
                cite_block += f"\n**[{i}] {c['file']}**\n> {c['excerpt']}...\n"
        else:
            cite_block = "\n\n---\n*No matching sources found in knowledge base.*"
        return answer + cite_block
    except Exception as e:
        return f"✗ Error: {str(e)}"

with gr.Blocks(
    title="OpsGPT — Private IT Knowledge Base",
    css=CUSTOM_CSS,
    theme=gr.themes.Base(
        primary_hue="green",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("DM Sans"),
    )
) as demo:

    with gr.Row(elem_classes=["main-wrap"]):

        # ── Sidebar ──────────────────────────────
        with gr.Column(elem_classes=["sidebar-col"]):

            gr.Markdown("**Ops**GPT", elem_id="logo-md")
            gr.Markdown("// PRIVATE IT KNOWLEDGE BASE", elem_id="logo-sub")

            gr.Markdown("KNOWLEDGE BASE", elem_classes=["section-label"])
            load_btn = gr.Button("⊕ Load Demo Data", variant="primary")
            status = gr.Textbox(
                label="Status",
                interactive=False,
                lines=3,
                value="No documents loaded.\nClick Load Demo Data to begin.",
                elem_id="status-box"
            )
            load_btn.click(initialize_with_demo, outputs=[status])

            gr.Markdown("UPLOAD DOCUMENTS", elem_classes=["section-label"])
            file_upload = gr.File(
                label="Drop PDF · TXT · MD",
                file_count="multiple",
                file_types=[".pdf", ".txt", ".md"],
            )
            ingest_btn = gr.Button("↑ Ingest Documents", variant="secondary")
            ingest_status = gr.Textbox(
                label="Ingest Status",
                interactive=False,
                lines=2,
                value=""
            )
            ingest_btn.click(upload_and_ingest, inputs=[file_upload], outputs=[ingest_status])

            gr.Markdown(
                "MODEL · llama3:8b · local\n\nEMBED · all-MiniLM-L6-v2\n\nINDEX · FAISS · MMR k=5",
                elem_id="logo-sub"
            )

        # ── Chat ──────────────────────────────────
        with gr.Column(elem_classes=["chat-col"]):

            gr.Markdown(
                "● LLAMA 3 ACTIVE &nbsp;·&nbsp; FAISS INDEX READY &nbsp;·&nbsp; 0 DATA EGRESS &nbsp;·&nbsp; 100% LOCAL",
                elem_id="chat-header"
            )

            gr.ChatInterface(
                fn=chat,
                examples=[
                    "How do I reset a user's MFA in Azure AD?",
                    "What is the escalation path for a P1 network outage?",
                    "How do I install the VPN client on macOS?",
                    "What do I do if a user clicks a phishing link?",
                    "What is the IT onboarding checklist for a new employee?",
                    "How do I troubleshoot file share connectivity issues?",
                ],
                cache_examples=False,
                chatbot=gr.Chatbot(
                    height=520,
                    placeholder="<div style='text-align:center;color:#6b7585;font-family:JetBrains Mono,monospace;font-size:12px;padding:60px 20px'><div style='font-size:32px;margin-bottom:16px'>🖥</div><div style='font-size:14px;color:#e4e8f0;margin-bottom:8px'>Ask anything about your IT documentation</div>Load the demo knowledge base or upload your own runbooks, then ask a question. Every answer is grounded in your documents with cited sources.</div>",
                    show_label=False,
                ),
                textbox=gr.Textbox(
                    placeholder="Ask a question about your IT documentation...",
                    show_label=False,
                    lines=1,
                    elem_classes=["input-row"],
                ),
                submit_btn="Send →",
            )

if __name__ == "__main__":
    demo.launch(server_port=7860, share=False)