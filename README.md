<img width="1915" height="926" alt="image" src="https://github.com/user-attachments/assets/dc721ff2-5657-41f6-b75d-ab2d33370bf8" />

# 🎓 AI Tutor for Students (Hybrid RAG)

AI Tutor is an interactive learning assistant built with Streamlit.  
It summarizes study materials, answers questions like a personal tutor, and generates quizzes (MCQ + True/False) with explanations.

## Supported Sources

- PDF files
- Website articles
- Web search
- Hybrid RAG system for accuracy (material + online sources)

---

## 🔐 Requirements (Before Running)

| API | Purpose | Required? | Link | Free Trial |
|-----|---------|-----------|------|------------|
| Groq API Key | LLM for answers, summaries, quizzes | ✅ Yes | [Groq Console](https://console.groq.com) | ✅ Free trial available |
| Cohere API Key | Embeddings for higher accuracy | ✅ Optional | [Cohere Dashboard](https://dashboard.cohere.com) | ✅ Free trial available |

Enter your API keys directly in the Streamlit sidebar.  
Live Streamlit Demo: [https://hamdy-ai-tutor.streamlit.app](https://hamdy-ai-tutor.streamlit.app)

---

## Key Features

- Upload a PDF or URL and get a clean educational summary  
- Ask questions with source-aware answers  
- Quiz generator (MCQ + True/False) with explanations  
- Saves processing time and shows the source used  
- Can run locally or online using Streamlit Cloud  

---

## 🧠 How the AI Works (Simple Explanation)

The app uses a **multi-agent Hybrid RAG system** to pick the best information source.

**If you upload a PDF or a URL:**

- The app extracts text and splits it into small learning chunks  
- You can generate a summary or embeddings

**When you ask a question or generate a quiz:**

1. If embeddings exist → AI retrieves the related information  
2. If only a summary exists → AI uses the summary  
3. If neither exist → AI uses random chunks from the start and end of the material  

**If no material is added:**

- The AI searches the web using:
  - Wikipedia  
  - ArXiv research papers  
  - DuckDuckGo Search (DDGS)

✅ This ensures accurate answers even when material is limited.

---

## 🔧 Tools & Technologies Used

| Component | Technology / Model |
|-----------|-------------------|
| UI & Frontend | Streamlit |
| LLM / AI | openai/gpt-oss-120b |
| Embeddings | cohere-multilingual-v3.0 |
| Retrieval & Pipelines | LangChain |
| Vector Database | FAISS |
| PDF + Text Processing | PyPDF |
| Web Search | Wikipedia, DDGS, ArXiv |
| Storage | Local files / vector database |

The system uses a **Hybrid RAG pipeline** to automatically choose the best data source.

---

## 🚀 Run Locally

```bash
git clone https://github.com/Hamdy005/AI-Tutor
cd AI-Tutor
pip install -r requirements.txt
streamlit run app.py
