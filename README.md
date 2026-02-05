# 📊 TalkToDB: English-to-SQL AI Agent (Mini RAG)

TalkToDB is a production-minded AI Agent that enables users to interact with structured datasets (CSV/Excel) using natural language. This project was developed as part of the **Track B: AI Engineer Assessment ("Mini RAG")**.

---

## 🔗 Project Links
* **Live Demo:** https://sqlaiagent-ccvuvtaaw5hpcvozvwlloa.streamlit.app/
* **Resume:** https://drive.google.com/drive/folders/1GsxxaNR3G8elRgOFCoNHgsvU8zuJdh8F?usp=drive_link

---

## 🏗️ Architecture & Workflow



The application implements a specialized RAG workflow for structured data:

1. **Dynamic Data Ingestion:** Users upload a CSV/Excel file via the frontend, which is immediately converted into a local SQLite table.
2. **Schema Indexing:** Table definitions (table names and column headers) are extracted and stored in a **ChromaDB Vector Store** using HuggingFace `all-MiniLM-L6-v2` embeddings.
3. **Contextual Retrieval:** When a user asks a question, the **Retriever** identifies the most relevant table schemas from the Vector DB.
4. **SQL Generation:** The user query and retrieved schema are passed to **Groq (Llama 3.3)** to generate an accurate SQL query.
5. **Grounded Answering:** The SQL result is passed back to the LLM to provide a natural language response with **inline citations** (e.g., [1]) mapping back to the source tables.

---

## 🛠️ Technical Stack
* **Frontend:** Streamlit
* **LLM Provider:** Groq Cloud (Llama-3.3-70b-versatile)
* **Vector Database:** ChromaDB
* **Orchestration:** LangChain
* **Embeddings:** HuggingFace `all-MiniLM-L6-v2`

---

## 🚀 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/your-username/sql-ai-agent.git](https://github.com/your-username/sql-ai-agent.git)
   cd sql-ai-agent
