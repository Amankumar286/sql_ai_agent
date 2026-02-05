import sqlite3
import pandas as pd
import os
import shutil
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

def ingest_schema():
    """
    Ingest database schema into vector store for RAG retrieval.
    FIX: Better error handling and detailed schema information
    """
    try:
        # Check if database exists
        if not os.path.exists('database.db'):
            print("⚠️ Database not found. Please upload a file first.")
            return
        
        # Clear old vector database
        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db")
            print("🗑️ Cleared old vector database")
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("⚠️ No tables found in database")
            conn.close()
            return
        
        documents = []
        
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            
            try:
                # Get column information
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                if not columns:
                    continue
                
                # Format: column_name (type)
                column_info = []
                for col in columns:
                    col_name = col[1]
                    col_type = col[2]
                    column_info.append(f"{col_name} ({col_type})")
                
                # Get sample data
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                # Get first few rows to understand data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_rows = cursor.fetchall()
                
                # Create detailed schema document
                schema_doc = f"""Table Name: {table_name}

Columns:
{chr(10).join(['- ' + col for col in column_info])}

Row Count: {row_count}

Sample Data Available: Yes"""
                
                # Create document with metadata
                doc = Document(
                    page_content=schema_doc,
                    metadata={
                        "table": table_name,
                        "source": "database.db",
                        "columns": [col[1] for col in columns],
                        "row_count": row_count
                    }
                )
                documents.append(doc)
                print(f"✅ Indexed table: {table_name} ({len(column_info)} columns, {row_count} rows)")
            
            except Exception as e:
                print(f"⚠️ Error indexing table {table_name}: {e}")
                continue
        
        conn.close()
        
        if not documents:
            print("⚠️ No documents created for vector database")
            return
        
        # Create vector database
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_db = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        
        print(f"✅ Vector database created successfully with {len(documents)} table schemas!")
    
    except Exception as e:
        print(f"❌ Error in ingest_schema: {e}")

if __name__ == "__main__":
    ingest_schema()
