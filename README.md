# 🎓 AI Tutor for Students

AI Tutor is an interactive learning assistant built with Streamlit.  
It summarizes study materials, answers questions like a personal tutor, and generates quizzes (MCQ + True/False) with explanations.

Supports:
✅ PDF files  
✅ Website articles  
✅ Web search  
✅ Multi-agent RAG system for accuracy

---

## ✅ Key Features

✔ Upload a PDF or URL and get a clean educational summary  
✔ Ask questions with source-aware answers  
✔ Smart quiz generator:
- Multiple-choice + True/False
- Correct answers + explanations

✔ Intelligent Source Handling
| Available Data | AI Uses |
|----------------|--------|
| Embeddings | Most accurate retrieval |
| Summary only | Uses summary |
| Only text chunks | Uses start/end chunks |
| No material | Searches the web automatically |

---

## 🌐 Smart Web Search + Material Combination

The AI doesn’t rely only on uploaded material.  
It can **combine your study material with online knowledge** for the most accurate answer.

When you ask a question or generate a quiz:

✅ If you uploaded material:
- The AI uses your PDF/URL first  
- Then it can enhance answers using:
  - Wikipedia  
  - ArXiv research papers  
  - DuckDuckGo Search (DDGS)

✅ If no material is uploaded:
- It automatically switches to pure web search  
- You can still ask questions or generate quizzes  
- Results come from Wikipedia, ArXiv, and DDGS

This ensures accurate answers even with limited or no study files.

---

## 🔐 Requirements

| API | Purpose | Required? | Link | Free Trial |
|-----|---------|-----------|------|------------|
| Groq API Key | Runs LLM for answers, summaries, quizzes | ✅ Yes | https://console.groq.com | ✅ Free trial available |
| Cohere API Key | Generates embeddings for more accurate retrieval | ✅ Optional (recommended) | https://dashboard.cohere.com | ✅ Free trial available |

💡 Add your API keys directly from the Streamlit sidebar.

---

## 🚀 Run Locally

```bash
git clone <your-repo-url>
cd <project-folder>
pip install -r requirements.txt
streamlit run app.py
