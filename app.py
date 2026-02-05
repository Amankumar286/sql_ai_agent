import streamlit as st
import pandas as pd
import sqlite3
import time
import os
from datetime import datetime

# --- Import from your actual engine files ---
# Ensure engine.py and ingest.py are in the same directory
try:
    from engine import get_relevant_schema, generate_sql, execute_query, get_final_answer
    from ingest import ingest_schema
except ImportError as e:
    st.error(f"❌ Import Error: {e}. Please ensure 'engine.py' and 'ingest.py' are in the same directory.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="SQL AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling (Fixed Code Block Issue) ---
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    /* Global Settings */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Title Container */
    .title-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .title-text {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .subtitle-text {
        color: #f0f0f0 !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* --- Input Field Styling --- */
    /* White background, Black text for visibility */
    .stTextInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #dfe6e9;
        border-radius: 10px;
    }
    
    .stTextInput label {
        color: #000000 !important;
        font-weight: 600;
    }

    /* --- FIXED CODE BLOCK STYLING --- */
    /* Target Streamlit's code block specifically */
    [data-testid="stCodeBlock"] {
        background-color: #1e1e1e !important;
        border-radius: 10px !important;
        border: 2px solid #667eea !important;
        padding: 1rem !important;
    }
    
    [data-testid="stCodeBlock"] pre {
        background-color: transparent !important;
        color: #e0e0e0 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    
    [data-testid="stCodeBlock"] code {
        color: #e0e0e0 !important;
        background-color: transparent !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* --- Card Container for Input --- */
    .custom-card {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    .sidebar-header {
        color: #667eea;
        font-weight: 700;
        font-size: 1.2rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
        margin-bottom: 1rem;
    }

    /* --- Buttons --- */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    /* --- Expandable Containers --- */
    [data-testid="stExpander"] {
        background-color: white !important;
        border-radius: 10px !important;
        border: 1px solid #e0e0e0 !important;
        margin-bottom: 1rem !important;
    }
    
    [data-testid="stExpander"] details {
        background-color: white !important;
    }
    
    [data-testid="stExpander"] summary {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    [data-testid="stExpander"] div {
        color: #000000 !important;
    }

    /* --- Footer --- */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #636e72;
        font-size: 0.9rem;
        margin-top: 3rem;
    }

    /* --- Global Text Color Override (Excluding Code Blocks) --- */
    body, p, div, span, h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stText {
        color: #000000 !important;
    }

    /* Ensure dataframes and tables have black text */
    .stDataFrame, table, th, td {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* Ensure text in expanders is black */
    .streamlit-expanderHeader, .streamlit-expanderContent {
        color: #000000 !important;
    }
    
    /* Fix for any other potential code snippets */
    code:not([data-testid="stCodeBlock"] code) {
        background-color: #f0f0f0 !important;
        color: #d63384 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Custom SQL Display for better visibility */
    .sql-display {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 2px solid #667eea !important;
        font-family: 'Courier New', monospace !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        margin: 10px 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'query_history' not in st.session_state: st.session_state.query_history = []
if 'total_queries' not in st.session_state: st.session_state.total_queries = 0
if 'selected_query' not in st.session_state: st.session_state.selected_query = ""
if 'show_results' not in st.session_state: st.session_state.show_results = False
if 'last_result' not in st.session_state: st.session_state.last_result = None
if 'last_sql' not in st.session_state: st.session_state.last_sql = None
if 'last_time' not in st.session_state: st.session_state.last_time = 0

# --- Header ---
st.markdown("""
    <div class="title-container">
        <h1 class="title-text">🤖 SQL AI Agent</h1>
        <p class="subtitle-text">Upload your CSV/Excel file and ask questions in natural language</p>
    </div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">📁 Data Management</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload your file here",
        type=["csv", "xlsx"],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        with st.spinner("🔄 Processing file..."):
            try:
                # 1. Read Data
                if uploaded_file.name.endswith('.csv'):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                
                # 2. Save to SQLite (Default table name 'sales' for simplicity)
                conn = sqlite3.connect('database.db')
                df_upload.to_sql('sales', conn, if_exists='replace', index=False)
                conn.close()
                
                # 3. Update Vector DB
                try:
                    ingest_schema()
                except Exception as ingest_e:
                    st.warning(f"⚠️ Ingest Warning: {ingest_e}")
                
                st.success(f"✅ '{uploaded_file.name}' indexed successfully!")
                
                with st.expander("📊 View Data Preview"):
                    st.dataframe(df_upload.head(), use_container_width=True)
                    st.caption(f"Rows: {len(df_upload)} | Columns: {len(df_upload.columns)}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    st.markdown("---")
    st.markdown('<div class="sidebar-header">📊 Metrics</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Queries", st.session_state.total_queries)
    with col2:
        st.metric("Last Time", f"{st.session_state.last_time:.2f}s")
    
    # History
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown('<div class="sidebar-header">📜 History</div>', unsafe_allow_html=True)
        for i, h in enumerate(reversed(st.session_state.query_history[-5:])):
            if st.button(f"⏱️ {h['query'][:20]}...", key=f"hist_{i}"):
                st.session_state.selected_query = h['query']
                st.rerun()

# --- Main Interface ---

# Input Container
st.markdown('<div class="custom-card">', unsafe_allow_html=True)

query = st.text_input(
    "💬 Ask your question here:",
    value=st.session_state.selected_query,
    placeholder="e.g., 'What is the total sales amount?' or 'Find items with price > 100'",
    key="main_query_input"
)

# Clear selection to avoid stuck inputs
if st.session_state.selected_query:
    st.session_state.selected_query = ""

# Quick Buttons
st.markdown("### 🚀 Quick Queries")
qb1, qb2, qb3, qb4 = st.columns(4)
if qb1.button("📊 Total Sales", use_container_width=True): 
    query = "What is the total sales amount?"
    st.session_state.show_results = False
if qb2.button("🏙️ Sales by City", use_container_width=True): 
    query = "Show sales by city"
    st.session_state.show_results = False
if qb3.button("📈 Top Products", use_container_width=True): 
    query = "What are the top 5 products?"
    st.session_state.show_results = False
if qb4.button("📅 Avg Price", use_container_width=True): 
    query = "What is the average price?"
    st.session_state.show_results = False

# Generate Button
generate_button = st.button("🚀 Generate Query", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Logic Processing ---
if generate_button and query and not st.session_state.show_results:
    if not os.path.exists('database.db'):
        st.error("⚠️ Database not found! Please upload a file first.")
    else:
        with st.spinner("🔍 Analyzing your data..."):
            try:
                start_time = time.time()
                
                # 1. Get Schema
                schema_context, sources = get_relevant_schema(query)
                
                # 2. Generate SQL
                sql_query, gen_time = generate_sql(query, schema_context)
                
                if "ERROR" in sql_query:
                    st.error(f"❌ Could not generate SQL: {sql_query}")
                else:
                    # 3. Execute SQL
                    df_result, exec_error = execute_query(sql_query)
                    
                    if exec_error:
                        st.error(f"❌ Execution Error: {exec_error}")
                        with st.expander("Debug SQL"):
                            st.code(sql_query, language="sql")
                    else:
                        # Removed AI Answer generation to avoid vague responses
                        total_time = time.time() - start_time
                        
                        # Store State
                        st.session_state.last_result = df_result
                        st.session_state.last_sql = sql_query
                        st.session_state.last_time = total_time
                        st.session_state.total_queries += 1
                        st.session_state.query_history.append({'query': query, 'timestamp': datetime.now()})
                        st.session_state.show_results = True
                        st.rerun()
                        
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

# --- Result Display ---
if st.session_state.show_results and st.session_state.last_result is not None:
    
    # 1. Technical Details (Collapsible)
    with st.expander("🔧 View SQL Query & Raw Data", expanded=True):
        col1, col2 = st.columns([1,1])
        with col1:
            st.markdown("**Generated SQL:**")
            
            # Enhanced SQL display with custom styling
            sql_display = f"""
            <div class="sql-display">
            {st.session_state.last_sql}
            </div>
            """
            st.markdown(sql_display, unsafe_allow_html=True)
            
            # Also keep the original code block for copy functionality
            st.code(st.session_state.last_sql, language="sql")
            
        with col2:
            st.markdown(f"**Execution Time:** {st.session_state.last_time:.2f}s")
            st.markdown(f"**Rows Returned:** {len(st.session_state.last_result)}")
            st.markdown(f"**Columns:** {', '.join(st.session_state.last_result.columns.tolist())}")
        
        st.markdown("**Raw DataFrame:**")
        st.dataframe(st.session_state.last_result, use_container_width=True)

    # 2. Visualization (Auto)
    if not st.session_state.last_result.empty:
        with st.expander("📊 Data Visualization", expanded=True):
            numeric_cols = st.session_state.last_result.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                # Use first column as X-axis
                chart_data = st.session_state.last_result.set_index(st.session_state.last_result.columns[0])
                st.bar_chart(chart_data[numeric_cols])
            else:
                st.info("No numeric data to visualize.")

    # 3. New Query Button
    if st.button("🔄 Ask Another Question", use_container_width=True):
        st.session_state.show_results = False
        st.session_state.last_result = None
        st.session_state.last_sql = None
        st.rerun()

# --- Footer ---
st.markdown('<div class="footer">Made with ❤️ using Streamlit & Groq</div>', unsafe_allow_html=True)