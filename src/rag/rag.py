import os
from functools import lru_cache
from typing import Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchResults
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_openai import ChatOpenAI

from src.config import settings
from src.database import get_supabase


# ── Embeddings ─────────────────────────────────────────

EMBEDDING_DIM = 384

@lru_cache
def get_embedder():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def store_embeddings(material_id: str, chunk_ids: list[str], chunks: list[str]):
    embedder = get_embedder()
    embeddings = embedder.embed_documents(chunks)

    records = [
        {"chunk_id": cid, "material_id": material_id, "embedding": emb}
        for cid, emb in zip(chunk_ids, embeddings)
    ]

    db = get_supabase()
    for i in range(0, len(records), 50):
        db.table("material_embeddings").insert(records[i:i + 50]).execute()


def similarity_search(query: str, material_id: str, k: int = 5) -> list[dict]:
    embedder = get_embedder()
    query_embedding = embedder.embed_query(query)

    db = get_supabase()
    result = db.rpc(
        "match_material_chunks",
        {
            "query_embedding": query_embedding,
            "match_material_id": material_id,
            "match_threshold": 0.7,
            "match_count": k,
        },
    ).execute()

    return result.data


# ── LLM ────────────────────────────────────────────────

def get_llm():
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise ValueError("OPENROUTER_API_KEY not found. Please set it in config.env.")
    return ChatOpenAI(
        model=settings.model_name,
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
    )


# ── Web Search Tools ───────────────────────────────────

def web_search_tools():
    wikipedia = WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=7000)
    )
    arxiv = ArxivQueryRun(
        api_wrapper=ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=8000)
    )
    duck = DuckDuckGoSearchResults()
    return [wikipedia, arxiv, duck]


# ── Supabase Retriever (replaces FAISS) ────────────────

class SupabaseRetriever(BaseRetriever):
    material_id: str
    k: int = 4

    def _get_relevant_documents(self, query: str) -> list[Document]:
        results = similarity_search(query, self.material_id, self.k)
        return [
            Document(page_content=r["content"], metadata={
                "similarity": r.get("similarity"),
                "chunk_id": r.get("chunk_id"),
            })
            for r in results
        ]


# ── RAG Prompt ─────────────────────────────────────────

def _rag_prompt():
    return PromptTemplate(
        input_variables=["chat_history", "input", "agent_scratchpad"],
        template="""
You are an advanced AI research assistant specializing in accurate, well-reasoned, and context-aware responses.
You have access to multiple external tools including:

- **Wikipedia Retriever** for general knowledge and conceptual explanations,
- **Arxiv Retriever** for academic and scientific research information,
- **DuckDuckGo Retriever** for the latest web-based insights,
- **Knowledge Retriever:** for local learning materials, which may include:
    - Embedding-based vector databases (most precise and semantic),
    - Summaries (concise overviews of key material),
    - Raw text chunks (unedited extracted text, less refined but detailed).

## Role and Objectives:
- Provide clear, factual, and logically organized answers.
- Integrate information from available tools when relevant.
- Maintain a professional and instructive tone.
- Respect previous chat context to ensure continuity.

## Reasoning Guidelines:
1. Use retrievers only when they can enhance or verify your response.
2. Combine retrieved facts with your own reasoning.
3. When multiple tools return information, synthesize a unified explanation.
4. If information is insufficient, acknowledge the limitation.
5. Always focus on clarity, structure, and factual accuracy.

## Response Format:
- **1. Informed Answer:** Provide a detailed, structured explanation.
- **2. Final Insight:** Conclude with a short, relevant takeaway.

---
### Chat History:
{chat_history}

### User Query:
{input}

### Agent Scratchpad:
{agent_scratchpad}
""",
    )


# ── RAG Answer ─────────────────────────────────────────

def rag_answer(
    query: str,
    material_id: Optional[str] = None,
    chunks: Optional[list[str]] = None,
    summaries: str = "",
    memory: ConversationBufferMemory = None,
):
    if memory is None:
        memory = ConversationBufferMemory(
            input_key="input", memory_key="chat_history", return_messages=True
        )

    prompt = _rag_prompt()
    tools = web_search_tools()
    llm = get_llm()

    if material_id:
        retriever = SupabaseRetriever(material_id=material_id, k=4)
        retriever_tool = create_retriever_tool(
            retriever,
            name="knowledge_retriever",
            description="Retrieves relevant educational material, notes, and explanations from the knowledge base.",
        )
        tools.append(retriever_tool)

    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,
        return_intermediate_steps=False,
        handle_parsing_errors=True,
    )

    response = executor.invoke({"input": query})
    return response["output"], memory
