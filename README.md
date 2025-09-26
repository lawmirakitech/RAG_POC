
---

# 📘 RAG POC – Retrieval-Augmented Generation Assistant

This is a **Proof of Concept (POC)** for a Retrieval-Augmented Generation (RAG) application.
It allows you to ingest content from **PDFs** and **URLs** into a **Weaviate Vector Database**, and then perform question answering using **LangChain** and **OpenAI models**.

The frontend provides an intuitive **Streamlit UI**, while the backend is powered by **FastAPI**.

---

## ⚡ Features

* 📄 Ingest PDFs and URLs into **Weaviate vector database**
* 🤖 Query using **LangChain + OpenAI**
* 🧠 Uses **Hugging Face Embeddings** for vector representation
* 🖥️ Frontend built with **Streamlit**
* ⚙️ Backend powered by **FastAPI**
* 🐳 Full Docker support for easy deployment
* 🔍 Web scraping & PDF parsing support
* 🛠️ Modular coding (not strictly SOLID, but clean separation)
* 🔑 Environment variables managed via `.env` file
* 📝 Logging enabled (console-only)

---

## 🏗️ Technologies & Practices Used

* **Weaviate Vector Database**
* **LangChain**
* **FastAPI**
* **Streamlit**
* **Docker**
* **Hugging Face Embeddings**
* **Git & GitHub**
* **Web Scraping**
* **PDF Parsing (PyMuPDF/fitz)**
* **Conda for Environment Management**
* **Console Logging**
* **Makefile for automation**

---

## ⚠️ Limitations

* 📄 Uses a **basic PDF parser (`fitz`)**
* 🧠 **Conversation memory limited** (LangChain `ConversationBufferWindowMemory` with \~5 turns)
* ✅ Only **basic testing** done
* ✂️ **Fixed chunking** with hardcoded chunk size & overlap
* 🛠️ Not production-ready (POC level only)

---

## 📂 Project Structure

```
RAG_POC/
│── backend/        # FastAPI backend
│── frontend/       # Streamlit frontend
│── environment.yml # Conda environment dependencies
│── docker-compose.yml
│── Makefile
│── .env            # Environment variables (ignored in git)
```

---

## 🔑 Environment Setup

### 1. Clone Repository

```bash
git clone <repo-url>
cd RAG_POC
```

### 2. Setup Conda Environment (local dev)

We use `Makefile` to simplify commands.

```bash
make setup-env
make activate-env
```

This creates and activates a conda env named `rag_env` using `environment.yml`.

---

## ⚙️ Environment Variables

A `.env` file is required at the project root:

Example (`.env.template`):

```env
# Weaviate
WEAVIATE_URL=https://your-weaviate-instance.weaviate.network
WEAVIATE_API_KEY=your_weaviate_key

# OpenAI
OPENAI_API_KEY=your_openai_key
```

👉 Copy `.env.template` → `.env` and fill in values:

```bash
cp .env.template .env
```

---

## 🐳 Running with Docker

### 1. Build Containers

```bash
make docker-build
```

### 2. Run Containers

```bash
make docker-up
```

Runs both backend (FastAPI) and frontend (Streamlit).

* Backend → [http://localhost:8000/docs](http://localhost:8000/docs)
* Frontend → [http://localhost:8501](http://localhost:8501)

### 3. Stop Containers

```bash
make docker-down
```

---

## 🖥️ Running Locally (without Docker)

### Backend

```bash
make run-backend
```

Runs FastAPI on `http://localhost:8000`.

### Frontend

```bash
make run-frontend
```

Runs Streamlit on `http://localhost:8501`.

---

## 🛠️ Useful Make Commands

```bash
make setup-env        # Create conda env
make docker-build     # Build docker containers
make docker-up        # Run docker containers
make docker-down      # Stop containers
make run-backend      # Run backend locally
make run-frontend     # Run frontend locally
make clean            # Remove __pycache__
```

---

## ✅ Next Steps / Improvements

* Use **advanced PDF parsing**
* Implement **dynamic chunking**
* Add **persistent logging**
* Strengthen **test coverage**
* Explore **more robust memory** options

---

📌 This project is a **POC** and meant for learning & exploration of RAG workflows.

---

**Interface looks something like this**

![alt text](<Screenshot 2025-09-26 at 4.57.16 PM.png>)