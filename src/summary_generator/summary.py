import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from src.rag.rag import get_llm


def summarizer_prompt():
    return PromptTemplate(
        input_variables=["input"],
        template="""
You are an expert academic assistant tasked with creating a comprehensive and well-structured summary of educational material.

**INSTRUCTIONS:**
1. Analyze the provided text and identify the main topics, key concepts, and important details.
2. Create a coherent summary that flows logically from introduction to conclusion.
3. Focus on educational value - highlight definitions, theories, examples, and practical applications.
4. Maintain academic tone while ensuring clarity and accessibility.
5. Organize the summary with clear sections and logical progression.
6. If the content contains a list of facts, make sure the final summary presents them as a numbered list.

**STRUCTURE YOUR SUMMARY AS FOLLOWS:**
- **Overview**: Begin with a 2-3 sentence high-level overview of the entire content
- **Key Topics**: List the main topics covered in the material (Use a NUMBERED LIST: 1. , 2. , 3. ...)
- **Detailed Summary**: Provide a comprehensive section-by-section summary covering all important concepts
- **Key Takeaways**: Highlight the most important points, definitions, and conclusions (Use a NUMBERED LIST: 1. , 2. , 3. ...)
- **Educational Value**: Explain how this material helps in understanding the subject

**FORMATTING RULES:**
- Do NOT use markdown tables or pipe characters (|)
- Do NOT use separator lines (---, ===)
- Use [[[[### HEADER ###]]]] for Main Section Headings (e.g. [[[[### Detailed Summary ###]]]])
- Use [[[[>>> HEADER <<<]]]] for Sub-topics or Sub-headings inside a section (e.g. [[[[>>> Introduction <<<]]]])
- Do NOT put punctuation (like colons or periods) at the end of the text inside the markers.
- Use **Text** for important keywords, topics, or terms you want to highlight within paragraphs.
- Use numbered lists or bullet points instead of tables

**CONTENT TO SUMMARIZE:**
{input}

**REMEMBER:**
- Be thorough but concise
- Maintain academic accuracy
- Use clear, educational language
- Focus on what would be most helpful for a student studying this material
- **STRICT RULE:** Ensure that the opening and closing brackets match EXACTLY in number. If you start with [[[[###, you MUST end with ###]]]]. Do not omit any brackets.
""",
    )


def clean_summary(text: str) -> str:
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Remove markdown table separator lines (e.g. |---|---|)
        if re.match(r'^[\s\|]*[-]{2,}[\s\|]*$', stripped):
            continue
        # If it's a table row, just keep it but maybe clean it up a bit
        if re.match(r'^\|.*\|$', stripped):
            parts = [p.strip() for p in stripped.split('|')]
            parts = [p for p in parts if p]
            line = ' | '.join(parts)
        # Note: We NO LONGER strip bold (**) here because the frontend uses it for styling
        cleaned.append(line)
    return '\n'.join(cleaned)


def summarizer(text: str) -> str:
    prompt = summarizer_prompt()
    llm = get_llm()
    chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    raw = chain.run(input=text)
    return clean_summary(raw)
