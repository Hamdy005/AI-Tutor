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
  <img src="https://github.com/user-attachments/assets/132212b6-6a14-4031-898d-cd527455cb3c" width="800"/>
</p>

### 📝 Summary Generator
<p align="center">
  <img src="https://github.com/user-attachments/assets/f15c27fe-a759-4abf-9591-d828d69e83ca" width="800"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/dc52f94d-cdb5-40b6-900c-41180a326bac" width = "800" />
</p>

### ❓ Ask the Tutor (Q&A)
<p align="center">
  <img src="https://github.com/user-attachments/assets/d21c3c17-5347-44fb-a225-6ba4b94be207" width="800"/>
</p>

### 🧪 Quiz Generator
<p align="center">
  <img src="https://github.com/user-attachments/assets/fc06dc60-369a-42b9-8a8e-46e5a3c83b0a" width="800"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/7fc8ae5a-8223-48f9-a908-b986107043dd" width="800"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/b7a886bf-faf1-4e97-aa9a-0eb8873d9f14" width="800"/>
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
