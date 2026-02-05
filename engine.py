import os
import sqlite3
import pandas as pd
import time
import re
from dotenv import load_dotenv
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Environment & API Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Vector DB Load
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

def get_relevant_schema(query):
    """
    Retrieve relevant table schema based on user query.
    FIX: Added error handling for empty vector DB
    """
    try:
        # Get top 3 most relevant schemas
        docs = vector_db.similarity_search(query, k=3)
        
        if not docs:
            # Fallback: Get all tables from database
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            schema_context = "Available tables:\n"
            for table in tables:
                schema_context += f"- {table[0]}\n"
            return schema_context, ["Database Tables"]
        
        schema_context = ""
        sources = []
        
        for i, doc in enumerate(docs, 1):
            schema_context += f"\n[Source {i}]\n{doc.page_content}\n"
            sources.append(doc.metadata.get('table', 'Unknown Table'))
        
        return schema_context, sources
    
    except Exception as e:
        print(f"Error in get_relevant_schema: {e}")
        return "", ["Error"]

def generate_sql(user_query, schema_context):
    """
    Generate SQL query using Groq LLM.
    FIX: Improved prompt, better SQL extraction, error handling
    """
    system_prompt = f"""You are an expert SQL Developer for SQLite databases.

Database Schema:
{schema_context}

Instructions:
1. Generate a valid SQLite query that answers the user's question
2. Return ONLY the SQL query - no explanations, no markdown, no backticks
3. Use table names exactly as provided in the schema
4. If the question cannot be answered with available schema, return: "ERROR: Cannot answer this question with available data"
5. Always use proper SQL syntax for SQLite
6. For aggregations, use: COUNT(), SUM(), AVG(), MAX(), MIN()
7. If joining tables, use explicit JOIN syntax
8. Add LIMIT 100 to prevent huge result sets"""

    try:
        start_time = time.time()
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0,
            max_tokens=500,
        )
        
        generation_time = time.time() - start_time
        
        # FIX: Better SQL extraction and cleaning
        raw_sql = completion.choices[0].message.content.strip()
        
        # Remove markdown code blocks
        clean_sql = re.sub(r'```(?:sql|SQL)?', '', raw_sql).strip()
        clean_sql = clean_sql.replace('`', '').strip()
        
        # Remove common LLM artifacts
        clean_sql = re.sub(r'^(Here|Here\'s|The|This).*?(?:query|SQL)[:;]?\s*', '', clean_sql, flags=re.IGNORECASE)
        clean_sql = clean_sql.strip()
        
        # FIX: Handle multi-line queries
        clean_sql = ' '.join(clean_sql.split())
        
        print(f"Generated SQL: {clean_sql}")
        return clean_sql, generation_time
    
    except Exception as e:
        print(f"Error in generate_sql: {e}")
        return f"ERROR: {str(e)}", 0

def execute_query(sql_query):
    """
    Execute SQL query against SQLite database.
    FIX: Better error handling and validation
    """
    try:
        # Check for error markers
        if "ERROR" in sql_query.upper():
            return None, sql_query
        
        # Validate query is not empty
        if not sql_query or len(sql_query.strip()) < 5:
            return None, "Query is empty or too short"
        
        # Ensure database exists
        if not os.path.exists('database.db'):
            return None, "Database file not found. Please upload a file first."
        
        conn = sqlite3.connect('database.db')
        
        try:
            # FIX: Correct pandas function name
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            
            if df.empty:
                return df, None
            
            return df, None
        
        except sqlite3.OperationalError as e:
            conn.close()
            return None, f"SQL Error: {str(e)}. Please check table and column names."
        
        except Exception as e:
            conn.close()
            return None, f"Execution Error: {str(e)}"
    
    except Exception as e:
        return None, f"Database Connection Error: {str(e)}"

def get_final_answer(user_query, data_df, sources):
    """
    Generate final answer with inline citations.
    FIX: Better formatting and error handling
    """
    try:
        if data_df is None or data_df.empty:
            return "❌ No data found matching your query. Try rephrasing your question."
        
        data_str = data_df.to_string(index=False)
        
        # Create citation text
        citation_text = " | ".join([f"[{i+1}] {source}" for i, source in enumerate(set(sources))])
        
        prompt = f"""Based on the following data, answer the user's question clearly and concisely.

User Question: {user_query}

Data Retrieved:
{data_str}

Sources: {citation_text}

Instructions:
1. Answer the question directly using only the provided data
2. Include inline citations like [1], [2] etc. where relevant
3. Format numbers with proper formatting (currency, percentages, etc.)
4. Be concise and clear
5. If data shows totals/sums, highlight them"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
        )
        
        answer = completion.choices[0].message.content
        return answer
    
    except Exception as e:
        return f"Error generating answer: {str(e)}"
