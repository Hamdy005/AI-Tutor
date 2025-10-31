# 🎓 AI Tutor for Students (Hybrid RAG)

AI Tutor is an interactive learning assistant built with Streamlit.  
It summarizes study materials, answers questions like a personal tutor, and generates quizzes (MCQ + True/False) with explanations.

✅ Live Streamlit Demo: https://hamdy-ai-tutor.streamlit.app  

Supports:

✅ PDF files  
✅ Website articles  
✅ Web search  
✅ **Hybrid RAG system** for accuracy (material + online sources)

---

## 🔐 Requirements (Before Running)

| API | Purpose | Required? | Link | Free Trial |
|-----|---------|-----------|------|------------|
| Groq API Key | LLM for answers, summaries, quizzes | ✅ Yes | https://console.groq.com | ✅ Free trial available |
| Cohere API Key | Embeddings for higher accuracy | ✅ Optional | https://dashboard.cohere.com | ✅ Free trial available |

Enter your API keys directly in the Streamlit sidebar.

---

## ✅ Key Features

✔ Upload a PDF or URL and get a clean educational summary  
✔ Ask questions with source-aware answers  
✔ Quiz generator (MCQ + True/False) with explanations  
✔ Saves processing time and shows the source used  
✔ Can run locally or online using Streamlit Cloud  

---

## 🌐 Smart Web Search + Material Combination (Hybrid RAG)

The AI doesn’t rely only on uploaded material.  
It can **combine your study material with online knowledge (Hybrid RAG)** for the most accurate answer.

When answering questions or generating quizzes:

✅ If uploaded material exists:
- Uses your PDF/URL first  
- Can enhance answers using:
  - Wikipedia  
  - ArXiv research papers  
  - DuckDuckGo Search (DDGS)

✅ If no material is uploaded:
- AI automatically searches the web  
- Uses Wikipedia, ArXiv, and DDGS  
- You can still ask questions and generate quizzes

---

## 🔧 Tools & Technologies Used

| Component | Technology / Model |
|-----------|-------------------|
| UI & Frontend | Streamlit |
| LLM / AI | **Groq – gpt-oss-120b** |
| Embeddings | **Cohere – cohere-multilingual-v3.0** |
| Retrieval & pipelines | LangChain |
| Vector Database | **FAISS** |
| PDF + Text Processing | PyPDF |
| Web Search | Wikipedia, DDGS, ArXiv |
| Storage | Local files / vector database |

The system uses a **Hybrid RAG pipeline** to automatically choose the best data source.

---

## 🚀 Run Locally

```bash
git clone <your-repo-url>
cd <project-folder>
pip install -r requirements.txt
streamlit run app.py
