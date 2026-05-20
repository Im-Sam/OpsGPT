from typing import Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS

SYSTEM_PROMPT = """You are OpsGPT, a senior IT operations assistant with deep expertise in enterprise infrastructure, Azure, networking, security, and DevOps.

Answer questions using ONLY the context provided below. Be concise and direct. Format steps as numbered lists. If you cannot find the answer in the context, say: I do not have that information in the loaded documents. Try uploading the relevant runbook.

Do NOT make up information. Do NOT reference knowledge outside the provided context.

Context:
{context}

Question: {question}

Answer:"""

PROMPT = PromptTemplate(
    template=SYSTEM_PROMPT,
    input_variables=["context", "question"],
)

def build_chain(vectorstore: FAISS, top_k: int = 5):
    llm = OllamaLLM(
        model="llama3",
        temperature=0.1,
        num_predict=512,
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": top_k, "fetch_k": top_k * 3},
    )
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )
    return {"chain": chain, "retriever": retriever}

def query(chain_dict: dict, question: str) -> Dict[str, Any]:
    chain = chain_dict["chain"]
    retriever = chain_dict["retriever"]

    docs = retriever.invoke(question)
    answer = chain.invoke(question)

    seen = set()
    citations = []
    for doc in docs:
        src = doc.metadata.get("source_file", "Unknown")
        excerpt = doc.page_content[:200].replace("\n", " ").strip()
        key = (src, excerpt[:50])
        if key not in seen:
            seen.add(key)
            citations.append({
                "file": src,
                "excerpt": excerpt,
                "page": doc.metadata.get("page", "—"),
            })
    return {
        "answer": answer,
        "citations": citations,
        "num_sources": len(citations),
    }