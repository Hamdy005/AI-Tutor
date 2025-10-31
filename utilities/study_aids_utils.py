import os, re, json, random
from .rag_utils import web_search_agents
from langchain_core.tools import create_retriever_tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq

def get_llm():

    groq_api_key = os.environ.get("GROQ_API_KEY", "")

    if not groq_api_key:
        raise ValueError("Groq API key not found. Please set it in Streamlit sidebar.")
    
    os.environ['GROQ_API_KEY'] = groq_api_key
    return ChatGroq(model = 'openai/gpt-oss-120b')

def summarizer_prompt():

    summary_prompt = PromptTemplate(

        input_variables = ['input'],
        template = """
            You are an expert academic assistant tasked with creating a comprehensive and well-structured summary of educational material.

            **INSTRUCTIONS:**
            1. Analyze the provided text and identify the main topics, key concepts, and important details.
            2. Create a coherent summary that flows logically from introduction to conclusion.
            3. Focus on educational value - highlight definitions, theories, examples, and practical applications.
            4. Maintain academic tone while ensuring clarity and accessibility.
            5. Organize the summary with clear sections and logical progression.
            6. If the content contains a list of facts (like "10 facts about X"), make sure the final summary presents them as a numbered list.

            **STRUCTURE YOUR SUMMARY AS FOLLOWS:**
            - **Overview**: Begin with a 2-3 sentence high-level overview of the entire content
            - **Key Topics**: List the main topics covered in the material
            - **Detailed Summary**: Provide a comprehensive section-by-section summary covering all important concepts
            - **Key Takeaways**: Highlight the most important points, definitions, and conclusions
            - **Educational Value**: Explain how this material helps in understanding the subject

            - Summary Length Guidance:
            - small: ~300 tokens
            - medium: ~500-700 tokens
            - very large: ~1000 tokens

            **CONTENT TO SUMMARIZE:**
            {input}

            **REMEMBER:**
            - Be thorough but concise
            - Maintain academic accuracy
            - Use clear, educational language
            - Focus on what would be most helpful for a student studying this material
        """
    )

    return summary_prompt

def summarizer(text):

    prompt = summarizer_prompt()
    llm = get_llm()

    summary_chain = LLMChain(

        llm=llm,
        prompt=prompt,
        verbose=True

    )

    answer = summary_chain.run(input=text)
    return answer


def smart_quiz_prompt():

    template = """

        You are an expert quiz generator specialized in creating educational and accurate quizzes
        based on study materials or online information.

        **SOURCE PRIORITY:**
        1. If a retriever tool is available (e.g., embeddings), use it to access the material.
        2. If a text summary or chunks are provided, rely on that context.
        3. If no material is available, use the topic/title provided to search online for reliable educational sources.

        **TASK:**
        Create a {difficulty}-level quiz based on the provided material or topic.

        Include exactly:
        - {mcq_count} multiple choice questions
        - {tf_count} true/false questions

        **QUESTION REQUIREMENTS:**
        - Each MCQ must have 4 plausible options (A, B, C, D).
        - Answers must **reference the labeled option** (e.g., `"answer": "A) 12.5 cm"`).
        - All questions must be factually correct.
        - Include concise explanations referencing material or credible sources.
        - Maintain academic tone and clarity.

        **OUTPUT FORMAT (MUST BE VALID JSON):**
        {{
            "quiz_type": "{source_type}",
            "difficulty": "{difficulty}",
            "mcq_count": {mcq_count},
            "tf_count": {tf_count},
            "mcq": [
                {{
                    "question": "Question text",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "answer": "A) Option A",
                    "explanation": "Brief factual explanation"
                }}
            ],
            "tf": [
                {{
                    "question": "True/False question text",
                    "answer": "True",
                    "explanation": "Brief factual explanation"
                }}
            ]
        }}



        **AVAILABLE CONTEXT:**
        {context}

        **THOUGHTS (optional):**
        {agent_scratchpad}
    """

    prompt = PromptTemplate(

        input_variables = ["difficulty", "mcq_count", "tf_count", "source_type", "context", "agent_scratchpad"],
        template = template

    )

    return prompt


def smart_quiz_generator(difficulty, mcq_count, tf_count, topic_title = None, vector_db = None, summary = None, chunks = None):

    # Preprocessing Chunks
    if chunks:
        random_chunks = random.sample(chunks, min(10, len(chunks) - 2)) + [chunks[0], chunks[-1]]
        random.shuffle(random_chunks)
        joined_chunks = "\n".join(random_chunks)

     # Using embeddings(vector DB) for quiz generation
    if vector_db:
        return contextual_quiz_generator(difficulty, mcq_count, tf_count, context = joined_chunks, vector_db = vector_db)


    # Using summary for quiz generation
    elif summary:
        return summary_quiz_generator(difficulty, mcq_count, tf_count, summary)
    

    # Using Chunks for quiz generation
    elif chunks:
        return summary_quiz_generator(difficulty, mcq_count, tf_count, joined_chunks)
    
    # Using Topic title to search the web
    elif topic_title:
        return web_quiz_generator(difficulty, mcq_count, tf_count, topic_title)

    else:
        raise ValueError("No data or topic provided for quiz generation.")


def summary_quiz_generator(difficulty, mcq_count, tf_count, summary_text):

    prompt = smart_quiz_prompt()
    llm = get_llm()

    chain = LLMChain(llm = llm, prompt = prompt)

    response = chain.run(

        difficulty = difficulty,
        mcq_count = mcq_count,
        tf_count = tf_count,
        source_type = "summary",
        context = summary_text,
        agent_scratchpad = ""
        
    )

    return _parse_quiz_response({"output": response})

def contextual_quiz_generator(difficulty, mcq_count, tf_count, context, vector_db):

    prompt = smart_quiz_prompt()
    llm = get_llm()

    vectordb_tool = create_retriever_tool(

        vector_db.as_retriever(),
        name = "quiz_material_retriever",
        description = "Retrieves relevant content from uploaded educational materials and documents for quiz generation."
        
    )

    tools_agent = create_openai_tools_agent(llm = llm, tools = [vectordb_tool], prompt = prompt)

    agent_executor = AgentExecutor(
        agent = tools_agent,
        tools = [vectordb_tool],
        verbose = True,
        return_intermediate_steps = False,
        handle_parsing_errors = True
    )


    response = agent_executor.invoke({

        "difficulty": difficulty,
        "source_type": "Document Embeddings", 
        "mcq_count": mcq_count,
        "tf_count": tf_count,
        "agent_scratchpad": "",
        "context": context

    })
    
    return _parse_quiz_response(response)



def web_quiz_generator(difficulty, mcq_count, tf_count, topic_title):
   
    prompt = smart_quiz_prompt()
    llm = get_llm()
    
    tools = web_search_agents()
    tools_agent = create_openai_tools_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(

        agent = tools_agent,
        tools = tools,
        verbose = True,
        return_intermediate_steps = False,
        handle_parsing_errors = True

    )       

    response = agent_executor.invoke({

        "context": topic_title,
        "difficulty": difficulty,
        "mcq_count": mcq_count,
        "tf_count": tf_count,
        "source_type": "Web Search",
        "agent_scratchpad": ""

    })

    return _parse_quiz_response(response)

def _parse_quiz_response(response):

    output_text = response['output'] if isinstance(response, dict) else str(response)

    # Cleaning and Matching the json object
    cleaned_output = re.sub(r"```(?:json)?\n?", "", output_text)
    cleaned_output = cleaned_output.replace("```", "").strip()
    
    m = re.search(r"(\{[\s\S]*\})", cleaned_output)
    if m:
        cleaned_output = m.group(1)

    quiz_dict = json.loads(cleaned_output)
    return quiz_dict
