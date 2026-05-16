# <img src="client/public/icon.svg" width="28" height="28" alt="icon"/> Study Buddy

AI Tutor is a Next.js AI tutor powered by FastAPI and Supabase. Upload PDFs and URLs to generate structured summaries, multi-session chat, and custom quizzes. Custom topics use web search through Wikipedia, ArXiv, and DuckDuckGo.

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

You can upload a **PDF**, provide a **URL**, or enter a **custom topic** — the system generates embeddings (for PDFs and URLs) or uses web search (for custom topics) to power all the features below.

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
  <img src="https://github.com/user-attachments/assets/df7a002f-eabe-41e8-b0d3-9a51c7ba5b94" alt="Google Sign-In" width="800"/>
</p>

### 🏠 Main Dashboard
<p align="center">
  <img src="https://github.com/user-attachments/assets/46e98ff1-1933-4688-8285-e5b30018023c" alt="Main Dashboard" width="800"/>
</p>

### 📝 Generated Summary
<p align="center">
  <img src="https://github.com/user-attachments/assets/a9204089-3b5b-424f-96a4-ee6f8be4723c" alt="Generated Summary" width="800"/>
  <img src="https://github.com/user-attachments/assets/b5d121d3-f86a-4402-83f5-dc3e8e430ae6" alt="Generated Summary" width="800"/>
</p>

### 💬 Chat Session
<p align="center">
  <img src="https://github.com/user-attachments/assets/8fb35724-fcf6-40d1-87c9-76e4f0c4eda5" alt="Chat Session with multiple sessions" width="800"/>
</p>

### 🧪 Quiz
<p align="center">
  <img src="https://github.com/user-attachments/assets/0afae1eb-c5f5-48a7-90f5-b3e67d13cad9" alt="Generate Quiz" width="800"/>
  <img src="https://github.com/user-attachments/assets/3fedae5c-5acc-4175-9b94-4d4afe5d1b39" alt="Generated Quiz" width="800"/>
  <img src= "https://github.com/user-attachments/assets/9e9cd452-388e-4a03-8176-532d4c306b16" alt="Quiz Results" width="800"/>
</p>

### 📄 Export PDF (Quiz)
<p align="center">
  <img src="https://github.com/user-attachments/assets/161dfae0-032c-4ce3-bdfd-a51284a15211" alt="Export Quiz as PDF" width="800"/>
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
