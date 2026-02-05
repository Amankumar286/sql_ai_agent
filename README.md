# 📊 TalkToDB — English-to-SQL AI Agent (Mini RAG)

**TalkToDB** is a production-minded **English-to-SQL AI Agent** that allows users to query structured datasets (CSV / Excel) using **natural language**.  
It implements a **Mini Retrieval-Augmented Generation (RAG)** pipeline tailored specifically for **tabular data**, enabling accurate SQL generation, execution, and grounded answers.

This project was built as part of **Track B: AI Engineer Assessment (Mini RAG)**.

---

## 🔗 Live Links

- 🚀 **Live Demo:**  
  https://sqlaiagent-ccvuvtaaw5hpcvozvwlloa.streamlit.app/

- 📄 **Resume & Portfolio:**  
  https://drive.google.com/drive/folders/1GsxxaNR3G8elRgOFCoNHgsvU8zuJdh8F

---

## ✨ Key Features

- 🗣️ Natural Language to SQL querying
- 📁 Upload CSV / Excel files dynamically
- 🧠 Schema-aware Mini RAG pipeline
- 🗄️ Automatic SQLite table creation
- 🔍 Vector-based schema retrieval using ChromaDB
- ⚡ Low-latency inference via Groq (Llama-3.3-70B)
- 📌 Grounded answers with inline citations
- 🧪 Production-oriented design and modular architecture

---

---

## 🏗️ Detailed Workflow

### 1️⃣ Dynamic Data Ingestion
- Users upload CSV or Excel files via Streamlit UI
- Files are parsed and converted into SQLite tables
- Supports multiple uploads per session

### 2️⃣ Schema Indexing
- Extracts table names, columns, and data types
- Schema metadata embedded using `all-MiniLM-L6-v2`
- Stored in ChromaDB for semantic retrieval

### 3️⃣ Contextual Retrieval
- User query is embedded
- Relevant table schemas retrieved
- Prevents hallucinated tables or columns

### 4️⃣ SQL Generation
- Retrieved schema + user query sent to Groq
- Uses **Llama-3.3-70B-Versatile**
- Generates safe, executable SQL

### 5️⃣ Grounded Answering
- SQL executed on SQLite database
- Results passed back to LLM
- Final response includes inline citations (e.g., [1])

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|-----------|
| Frontend | Streamlit |
| LLM Provider | Groq Cloud |
| Model | Llama-3.3-70B-Versatile |
| Vector Database | ChromaDB |
| Orchestration | LangChain |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Database | SQLite |

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/sql-ai-agent.git
cd sql-ai-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
GROQ_API_KEY=your_groq_api_key
streamlit run app.py
sql-ai-agent/
│
├── app.py
├── ingest.py
├── retriever.py
├── sql_generator.py
├── answer_generator.py
├── database/
│   └── local.db
├── requirements.txt
└── README.md

---

If you want next:
- 🔥 **ATS-optimized README**
- 🧠 **“Why this matters” section for recruiters**
- 📊 **Evaluation / accuracy metrics**
- 🧾 **System prompt & SQL guardrails section**

Just tell me 😄

## 🧠 System Architecture

