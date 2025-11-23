<img width="1915" height="926" alt="image" src="https://github.com/user-attachments/assets/dc721ff2-5657-41f6-b75d-ab2d33370bf8" />
<img width="1922" height="1039" alt="Summary" src="https://github.com/user-attachments/assets/31b47711-d68e-448b-aa2f-ef32cd8a1df0" />
<img width="1917" height="943" alt="Ask" src="https://github.com/user-attachments/assets/d21c3c17-5347-44fb-a225-6ba4b94be207" />
<img width="1918" height="847" alt="Quiz" src="https://github.com/user-attachments/assets/fc06dc60-369a-42b9-8a8e-46e5a3c83b0a" />
<img width="1920" height="1080" alt="Quiz Solution" src="https://github.com/user-attachments/assets/7fc8ae5a-8223-48f9-a908-b986107043dd" />
<img width="1920" height="1080" alt="Quiz Answers" src="https://github.com/user-attachments/assets/b7a886bf-faf1-4e97-aa9a-0eb8873d9f14" />



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
| Groq API Key | LLM for answers, summaries, quizzes | ✅ Yes | [Groq Console](https://console.groq.com) | ✅ Free Personal Key available |
| Cohere API Key | Embeddings for higher accuracy | ✅ Optional | [Cohere Dashboard](https://dashboard.cohere.com) | ✅ Free Personal Key available |<img width="1917" height="943" alt="Screenshot from 2025-11-23 22-54-07" src="https://github.com/user-attachments/assets/66398d16-3af7-47f0-9827-07762e1d3897" />


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
