# 🎓 AI Tutor for Students (Hybrid RAG)

AI Tutor is an interactive learning assistant built with Streamlit.  
It summarizes study materials, answers questions like a personal tutor, and generates quizzes (MCQ + True/False) with explanations.

## 📚 Supported Sources

- PDF files
- Website articles
- Web search
- Hybrid RAG system for accuracy (material + online sources)

## 🔐 Requirements (Before Running)

| API | Purpose | Required? | Link | Free Trial |
|-----|---------|-----------|------|------------|
| Groq API Key | LLM for answers, summaries, quizzes | ✅ Yes | [Groq Console](https://console.groq.com) | ✅ Free Personal Key available |


Enter your API keys directly in the Streamlit sidebar.  
**Live Streamlit Demo:** [https://hamdy-ai-tutor.streamlit.app](https://hamdy-ai-tutor.streamlit.app)

---

## 📸 Screenshots

### 🏠 Home Page
<p align="center">
  <img src="https://github.com/user-attachments/assets/e83ea2d2-9e1a-44aa-9a4b-6c7165ca230b" width="800"/>
</p>

### 📝 Summary Generator
<p align="center">
  <img src="https://github.com/user-attachments/assets/8520a7cc-09df-44f5-8f93-82711041761e" width="800"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/2a484af3-b699-4758-979d-86f9c46f0dfc" width = "800" />
</p>

### ❓ Ask the Tutor (Q&A)
<p align="center">
  <img src="https://github.com/user-attachments/assets/63723ca7-01ff-4f23-8e26-5669ef34ae6c" width="800"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/b550d0a6-6f99-4d51-bc03-ef7b69f3a2d4" width="800"/>
</p>

### 🧪 Quiz Generator
<p align="center">
  <img src="https://github.com/user-attachments/assets/b0b712ac-fe1a-400c-910c-35fc4ed56b10" width="800"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/a1319577-2b4f-46e8-9a00-1c36f5808177" width="800"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/57e03070-b33b-4718-b1fc-d3a9fc5932a4" width="800"/>
</p>
---

## ✨ Key Features

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
AI retrieves the related information using RAG-based embeddings.

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
| Embeddings | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Retrieval & Pipelines | LangChain |
| Vector Database | ChromaDB |
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
