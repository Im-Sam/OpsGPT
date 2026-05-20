# OpsGPT — Private IT Knowledge Base

> A fully local RAG (Retrieval-Augmented Generation) chatbot for IT operations teams. Ask questions about your internal runbooks, SOPs, and documentation — and get grounded, cited answers. No data leaves your machine.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-green)
![Ollama](https://img.shields.io/badge/Ollama-Llama%203-orange)
![FAISS](https://img.shields.io/badge/Index-FAISS-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## What It Does

OpsGPT lets you load your own IT documentation (runbooks, wikis, SOPs) and query it in natural language. Every answer is grounded exclusively in your documents — the model will not hallucinate or draw on external knowledge. Sources are cited inline with excerpts so you can verify every response.

**Designed for:**
- IT operations and helpdesk teams
- SREs managing internal runbooks
- Sysadmins who want searchable, conversational access to documentation

---

## Architecture

```
User Question
     │
     ▼
Gradio UI (app.py)
     │
     ▼
FAISS Retriever — MMR k=5  (embedder.py)
     │  top-k relevant chunks
     ▼
Prompt Template + Context
     │
     ▼
Llama 3 via Ollama  (chain.py)    ← 100% local, no API calls
     │
     ▼
Answer + Cited Sources
```

| Component | Technology |
|-----------|-----------|
| UI | Gradio |
| LLM | Llama 3 8B via Ollama |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Index | FAISS (MMR retrieval) |
| Document Loading | LangChain text splitters |
| Supported Formats | `.pdf`, `.txt`, `.md`, `.docx` |

---

## Prerequisites

1. **Python 3.10+**
2. **Ollama** installed and running — [ollama.com](https://ollama.com)
3. Llama 3 model pulled:
   ```bash
   ollama pull llama3
   ```

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/your-username/opsgpt.git
cd opsgpt

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Add your own documents
#    Drop .pdf / .txt / .md / .docx files into demo_data/

# 5. Run
python app.py
```

Then open [http://localhost:7860](http://localhost:7860) in your browser.

---

## Usage

### Option A — Demo Data
Click **⊕ Load Demo Data** in the sidebar. This ingests whatever documents are in the `demo_data/` folder, builds the FAISS index, and readies the chain. You can then ask questions immediately.

### Option B — Upload Your Own Documents
Use the **Drop PDF · TXT · MD** file uploader in the sidebar, then click **↑ Ingest Documents**. Your files are chunked, embedded, and added to the index. The chain rebuilds automatically.

### Asking Questions
Type any question into the chat input. Answers will include a **Sources** block at the bottom citing the originating file and a content excerpt for every retrieved chunk.

---

## Project Structure

```
opsgpt/
├── app.py              # Gradio UI, file upload handling, chat orchestration
├── rag/
│   ├── __init__.py
│   ├── chain.py        # LangChain RAG chain, prompt template, query + citation logic
│   ├── embedder.py     # HuggingFace embeddings, FAISS build/load/update
│   └── ingestor.py     # Document loading, chunking (RecursiveCharacterTextSplitter)
├── demo_data/          # Put your sample documents here (gitignored)
├── data/               # Auto-generated vectorstore index (gitignored)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Configuration

Key parameters and where to change them:

| Parameter | Location | Default | Description |
|-----------|----------|---------|-------------|
| LLM model | `chain.py` | `llama3` | Any model available in your Ollama install |
| LLM temperature | `chain.py` | `0.1` | Lower = more deterministic |
| Max tokens | `chain.py` | `512` | Max response length |
| Retrieval k | `chain.py` | `5` | Number of chunks returned per query |
| Chunk size | `ingestor.py` | `512` | Characters per document chunk |
| Chunk overlap | `ingestor.py` | `64` | Overlap between adjacent chunks |
| Embedding model | `embedder.py` | `all-MiniLM-L6-v2` | Any sentence-transformers model |
| Vectorstore path | `embedder.py` | `data/vectorstore` | Where FAISS index is saved |

---

## Privacy & Security

- **No data egress.** The LLM runs locally via Ollama. Embeddings are computed locally via `sentence-transformers`. Nothing is sent to any external API.
- **FAISS deserialization.** `embedder.py` loads the vectorstore with `allow_dangerous_deserialization=True`. This is safe because the index is always built locally from your own files. Do not load `.faiss` index files from untrusted sources with this flag.
- **Uploaded files** are written to `data/docs/uploads/` on disk. This directory is gitignored. Do not commit it.

---

## Requirements

```
gradio>=4.0.0
langchain>=0.2.0
langchain-ollama>=0.1.0
langchain-community>=0.2.0
langchain-huggingface>=0.0.3
langchain-text-splitters>=0.2.0
langchain-core>=0.2.0
faiss-cpu>=1.7.4
sentence-transformers>=2.7.0
```

---

## Roadmap

- [ ] Persistent chat history
- [ ] Multi-user session isolation
- [ ] Document deletion / index management UI
- [ ] Support for `.docx` upload via Gradio file picker
- [ ] Swap embedding model from UI
- [ ] Docker / `docker-compose` setup

---

## License

MIT — see `LICENSE` for details.
