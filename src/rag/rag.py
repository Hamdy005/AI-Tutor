import os
import asyncio
import uuid
import logging
from functools import lru_cache
from typing import Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchResults
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_openai import ChatOpenAI

from src.config import settings
from src.database import get_supabase
from src.store import get_chunks

logger = logging.getLogger(__name__)


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
    logger.info(f"Generating embeddings for material {material_id} ({len(chunks)} chunks)...")
    embedder = get_embedder()
    embeddings = embedder.embed_documents(chunks)

    records = [
        {"chunk_id": cid, "material_id": material_id, "embedding": emb}
        for cid, emb in zip(chunk_ids, embeddings)
    ]

    db = get_supabase()
    if db is None:
        logger.warning("Supabase not connected — embeddings computed but NOT stored (no DB).")
        return

    logger.info(f"Storing {len(records)} embeddings in Supabase...")
    for i in range(0, len(records), 50):
        db.table("material_embeddings").insert(records[i:i + 50]).execute()
    logger.info(f"Embeddings stored successfully for material {material_id}.")


def warmup_embedder():
    """Dummy forward pass to keep OpenMP/MKL thread pool alive during idle periods."""
    embedder = get_embedder()
    embedder.embed_documents(["warmup"])


async def store_embeddings_async(material_id: str, chunk_ids: list[str], chunks: list[str]):
    """
    Async variant of store_embeddings that routes embedding inference through
    the batch worker queue for batching across concurrent requests.
    """
    from src.rag.batch_workers import EmbeddingJob, embedding_queue, job_store

    job = EmbeddingJob(job_id=str(uuid.uuid4()), texts=chunks)
    await embedding_queue.put(job)
    await job.done.wait()

    entry = job_store[job.job_id]
    if entry["status"] == "error":
        raise RuntimeError(f"Embedding failed: {entry['error']}")

    embeddings = entry["result"]

    records = [
        {"chunk_id": cid, "material_id": material_id, "embedding": emb}
        for cid, emb in zip(chunk_ids, embeddings)
    ]

    db = get_supabase()
    if db is None:
        logger.warning("Supabase not connected — embeddings computed but NOT stored (no DB).")
        return

    logger.info(f"Storing {len(records)} embeddings in Supabase for material {material_id}...")
    for i in range(0, len(records), 50):
        db.table("material_embeddings").insert(records[i:i + 50]).execute()
    logger.info(f"Embeddings stored successfully for material {material_id}.")


def similarity_search(query: str, material_id: str, k: int = 5) -> list[dict]:
    embedder = get_embedder()
    query_embedding = embedder.embed_query(query)

    db = get_supabase()
    if db is None:
        return []
    
    result = db.rpc(
        "match_material_chunks",
        {
            "query_embedding": query_embedding,
            "match_material_id": material_id,
            "match_threshold": 0.35,
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


def get_groq_llm():
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in config.env.")
    return ChatOpenAI(
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        api_key=settings.groq_api_key,
        max_tokens=600,
    )


# ── Web Search Tools ───────────────────────────────────

def web_search_tools(has_material: bool = False):
    top_k = 1 if has_material else 2
    chars_max = 1500 if has_material else 4000
    
    wikipedia = WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(top_k_results=top_k, doc_content_chars_max=chars_max)
    )
    arxiv = ArxivQueryRun(
        api_wrapper=ArxivAPIWrapper(top_k_results=top_k, doc_content_chars_max=chars_max)
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

def _rag_prompt(has_tools: bool = True):
    tools_section = """
You have access to these tools:
- **Wikipedia Retriever** for general knowledge and conceptual explanations,
- **Arxiv Retriever** for academic and scientific research information,
- **DuckDuckGo Retriever** for the latest web-based insights,
- **Knowledge Retriever:** for local learning materials (vector embeddings, summaries, raw text chunks).
""" if has_tools else ""

    return PromptTemplate(
        input_variables=["chat_history", "input", "agent_scratchpad", "context"],
        template=f"""
You are a helpful AI study assistant. Your goal is to provide accurate, well-reasoned answers.

You have access to the following context to help you answer:

Context:
{{context}}
{tools_section}
## Instructions:
- Use the available context and tools to answer the user's question as thoroughly as possible.
- The "Context" section contains direct excerpts and information from the user's learning material. You MUST use this to answer questions, even if the "Chat History" is empty.
- Never claim you don't have information about the lecture or material just because the conversation has just started; always check the "Context" first.
- If you find relevant information in the context, synthesize it into a clear, well-structured answer.
- If the context partially answers the question, explain what you know and note any limitations.
- If the context and tools don't contain enough information, use your own knowledge to provide a helpful response and mention that it's based on general knowledge.
- Always provide educational value - explain concepts clearly.

## FORMATTING RULES:
- Do NOT use markdown tables or pipe characters (|)
- Do NOT use separator lines (---, ===)
- Use ### for Section Headings (e.g. ### Answer:)
- Use **Text** for important keywords, topics, or terms you want to highlight
- Use plain text with clear section labels followed by a colon (e.g. "Answer:", "Key Takeaway:")
- Use numbered lists or bullet points (with a dash -) instead of tables

## Response Format:
- Answer: Provide a detailed, structured explanation.
- Key Takeaway: Conclude with a short, relevant summary point.

---
### Chat History:
{{chat_history}}

### User Query:
{{input}}

### Agent Scratchpad:
{{agent_scratchpad}}
""",
    )


# ── RAG Answer ─────────────────────────────────────────

def rag_answer(
    query: str,
    material_id: Optional[str] = None,
    chunks: Optional[list[str]] = None,
    summaries: str = "",
    memory = None,
):
    if memory is None:
        memory = ConversationBufferWindowMemory(
            input_key="input", memory_key="chat_history", return_messages=True, k=5
        )

    # User requested: remove tool usage when material is uploaded, keep when not
    if material_id:
        tools = []
    else:
        tools = web_search_tools(has_material=False)

    prompt = _rag_prompt(has_tools=len(tools) > 0)
    llm = get_groq_llm()

    context_parts = []
    has_chunks = False

    if material_id:
        results = similarity_search(query, material_id, k=5)
        if results:
            has_chunks = True
            chunks = [r["content"] for r in results]
            context_parts.append(f"Relevant Excerpts:\n" + "\n---\n".join(chunks))

    # To save tokens, only pass the summary if no specific chunks were found
    if not has_chunks and summaries:
        context_parts.append(f"Material Summary (No specific excerpts found for your query):\n{summaries}")

    # Fallback: If NO chunks matched AND NO summary was generated, pass start and end chunks
    if not has_chunks and not summaries and material_id:
        all_chunks = get_chunks(material_id)
        if all_chunks:
            # Take first 3 and last 2 chunks
            head = all_chunks[:3]
            tail = all_chunks[-2:] if len(all_chunks) > 3 else []
            # Combine without duplicates
            sampled = head + [c for c in tail if c not in head]
            sampled_text = "\n---\n".join(c["content"] for c in sampled)
            context_parts.append(f"Material Sample (No summary found; showing start and end of material):\n{sampled_text}")

    context_str = "\n\n".join(context_parts) if context_parts else ""

    if tools:
        agent = create_openai_tools_agent(llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=False,
            return_intermediate_steps=False,
            handle_parsing_errors=True,
        )
        response = executor.invoke({"input": query, "context": context_str})
        return response["output"], memory
    else:
        # Simple LLM call without Agent loop to save tokens and avoid 429
        chain = prompt | llm
        
        # Load history from memory
        memory_vars = memory.load_memory_variables({"input": query})
        chat_history = memory_vars.get("chat_history", [])
        
        response = chain.invoke({
            "input": query,
            "context": context_str,
            "chat_history": chat_history,
            "agent_scratchpad": ""
        })
        
        answer = response.content
        # Save to memory manually
        memory.save_context({"input": query}, {"output": answer})
        return answer, memory

def extract_chat_title(query: str) -> str:
    llm = get_groq_llm()
    prompt = PromptTemplate(
        input_variables=["query"],
        template="Generate a very short, concise title (3-5 words max) for a chat session that starts with this user query: '{query}'. Do not use quotes or prefixes like 'Title:', just the title itself."
    )
    chain = prompt | llm
    response = chain.invoke({"query": query})
    title = response.content.strip().strip('"').strip("'")
    if len(title) > 50:
        title = title[:50].rsplit(' ', 1)[0] + '...'
    return title
