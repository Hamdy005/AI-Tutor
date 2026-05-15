# 🎓 Study Mate

AI Tutor is an interactive learning assistant — upload your study materials and get structured summaries, AI-powered chat, and custom quizzes.

---

## 🏗️ Architecture Overview

### 🌐 Frontend — Next.js

The UI is built with **Next.js** and deployed on **Vercel**, served under a custom domain. It supports **light and dark mode**: the default follows the **system preference**, and the user can override it with a manual toggle.

### ⚡ Backend — FastAPI

The AI engine runs on a **FastAPI** backend, handling embeddings, summarization, chat, and quiz generation.

### 🗄️ Database — Supabase

**Supabase** serves as the central database and vector store. All user data is persisted:

---

## ✨ Frontend Features

### 📝 Summary Generator

After generation, the summary is displayed as a **well-structured document** with **sub-header boxes** — each subtopic is stored in its own card for easy reading. Summaries can also be **exported**.

### 💬 Chat (Multi-Session)

- Users can create **multiple chat sessions**, each with its own context.
- Every chat session is **stored in the database** so it can be retrieved or revisited later.
- Chats are **exportable** in a pdf.

### 🧪 Quiz Generator

- Supports **True/False** and **MCQ** questions.
- Users can choose **any custom number of questions**.
- Quizzes are rendered in a **clean, good-looking UI** and can be **exported**.

---

## 🔐 Authentication

**Google OAuth** is used for all authentication — no custom passwords, usernames, or sign-up forms.

---

## 🧠 AI & Backend Details

### Embedding Pipeline

- Uses a **multilingual embedder** for cross-language support.
- When a material is uploaded, the system **processes it and generates embeddings asynchronously**, allowing **concurrent embedding of multiple materials** in parallel rather than sequentially.
- A **warm-up cycle** keeps the embedder active — ML models become idle without a forward pass for extended periods, so periodic warm-up prevents cold starts.

### Summary & Quiz Generation

- Uses **OpenRouter's API key** to generate summaries and quizzes based on material embeddings.
- If a **custom topic** is uploaded (instead of a PDF or URL), the topic text itself is used directly for generation.

### Chatbot

- Uses the **Groq API** (`llama-3.1-8b-instant`) for fast, low-latency responses.
- For **PDF and URL materials**, the chatbot replies using the stored **embeddings**.
- Each chat session gets an **auto-generated title** based on the first user message.
- For **custom topic** materials (no PDF/URL), the chatbot falls back to **web search tools** — **Wikipedia, ArXiv, and DuckDuckGo Search** — to retrieve relevant information.

### Rate Limits

- **Summary & Quiz generation** — 10 requests per day per user (uses OpenRouter).
- **Chatbot** — unlimited requests (uses Groq).

---

## 📸 Screenshots

### 🔑 Google Sign-In
<p align="center">
  <img src="YOUR_GOOGLE_SIGNIN_IMAGE_URL" alt="Google Sign-In" width="800"/>
</p>

### 🏠 Main Dashboard
<p align="center">
  <img src="YOUR_DASHBOARD_IMAGE_URL" alt="Main Dashboard" width="800"/>
</p>

### 📝 Generated Summary
<p align="center">
  <img src="YOUR_SUMMARY_IMAGE_URL" alt="Generated Summary" width="800"/>
</p>

### 💬 Chat Session
<p align="center">
  <img src="YOUR_CHAT_SESSION_IMAGE_URL" alt="Chat Session with multiple sessions" width="800"/>
</p>

### 🧪 Generated Quiz
<p align="center">
  <img src="YOUR_QUIZ_IMAGE_URL" alt="Generated Quiz" width="800"/>
</p>

### 📄 Export PDF (Quiz)
<p align="center">
  <img src="YOUR_EXPORT_PDF_IMAGE_URL" alt="Export Quiz as PDF" width="800"/>
</p>

---

## 🔧 Tools & Technologies

| Component | Technology |
|-----------|------------|
| Frontend | Next.js (Vercel + custom domain) |
| Backend | FastAPI (Python) |
| Database & Vector Store | Supabase |
| Summary & Quiz Model | `openai/gpt-oss-120b` via OpenRouter API |
| Chatbot Model | `llama-3.1-8b-instant` via Groq API |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Auth | Google OAuth |
| Web Search | Wikipedia, ArXiv, DuckDuckGo |
