import os, random, uuid
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.vectorstores import FAISS
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchResults
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.tools import Tool
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_groq import ChatGroq

@st.cache_resource(show_spinner=False)
def get_embedder():
    """Returns a cached HuggingFace embeddings model."""
    return HuggingFaceEmbeddings(
        model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )


def get_llm():

    groq_api_key = os.environ.get("GROQ_API_KEY", "")

    if not groq_api_key:
        raise ValueError("Groq API key not found. Please set it in Streamlit sidebar.")
    
    os.environ['GROQ_API_KEY'] = groq_api_key
    return ChatGroq(model = 'openai/gpt-oss-120b')

def create_vector_db(chunks):
    """Creates a FAISS vector database from text chunks."""
    
    embedder = get_embedder()
    vector_db = FAISS.from_texts(texts=chunks, embedding=embedder)
    return vector_db


def web_search_agents():

    wikipedia_wrapper = WikipediaAPIWrapper(top_k_results = 3, doc_content_chars_max = 7000)
    wikipedia_agent = WikipediaQueryRun(api_wrapper = wikipedia_wrapper)

    arxiv_wrapper = ArxivAPIWrapper(top_k_results = 2, doc_content_chars_max = 8000)
    arxiv_agent = ArxivQueryRun(api_wrapper = arxiv_wrapper)

    duckduckgo_agent = DuckDuckGoSearchResults()
    return [wikipedia_agent, arxiv_agent, duckduckgo_agent]

def rag_prompt():

    prompt = PromptTemplate(

        input_variables = ["chat_history", "input", "agent_scratchpad"],
        template = """

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
            - Your goal is to provide clear, factual, and logically organized answers to the user's queries.  
            - You must integrate information from the available tools when relevant.  
            - Maintain a professional and instructive tone — suitable for research or academic discussion.  
            - Respect previous chat context to ensure continuity and avoid redundancy.

            ## Reasoning Guidelines:
            1. Use **retrievers** only when they can enhance or verify your response.  
            2. Combine retrieved facts with your own reasoning — never rely solely on tool output.  
            3. When multiple tools return information, synthesize a unified, concise explanation.  
            4. If information is insufficient, acknowledge the limitation and reason based on known facts.  
            5. Always focus on **clarity, structure, and factual accuracy.**

            ## Response Format:
            Your response should follow this format:
            - **1. Informed Answer:** Provide a detailed, structured explanation that may combine reasoning with retrieved data.  
            - **2. Final Insight:** Conclude with a short, relevant takeaway or insight.

            ---

            ### Chat History:
            {chat_history}

            ### User Query:
            {input}

            ### Agent Scratchpad:
            {agent_scratchpad}

        """)

    return prompt

def rag_answer(query, chunks = [], summaries = '', vector_db = None, memory = None):

    if memory == None:
        memory = ConversationBufferMemory(input_key = 'input', memory_key = 'chat_history', return_messages = True)

    prompt = rag_prompt()
    tools = web_search_agents()
    llm = get_llm()
    
    # Creating the Vector Database Retriever tool
    vectordb_tool = create_retriever_tool(
        vector_db.as_retriever(),
        name = "knowledge_retriever",
        description = """
            Retrieves relevant educational material, notes, and explanations from the knowledge base 
            to help the tutor answer conceptual or factual questions accurately.     
        """
    )
        
    tools.append(vectordb_tool)

    tools_agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent = tools_agent,
        tools = tools,
        memory = memory, 
        verbose = True,
        return_intermediate_steps = False,
        handle_parsing_errors = True 
    )

    response = agent_executor.invoke({"input": query})
    return response['output'], memory