import os
import sys

# Add project root to system path to resolve imports correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import streamlit as st
from dotenv import load_dotenv
from src.database import db_manager
from src.agent import ask_agent, get_agent_config
from google.antigravity import Agent

# Load environment variables
load_dotenv()

# Map GOOGLE_API_KEY to GEMINI_API_KEY if needed (Google Antigravity SDK expects GEMINI_API_KEY)
if "GOOGLE_API_KEY" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

# Page Setup & SEO Best Practices
st.set_page_config(
    page_title="Graph-Relational AI Agent Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Directory to save conversation state for persistence
CHATS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.chats"))
os.makedirs(CHATS_DIR, exist_ok=True)

# Custom premium styling using HTML & CSS injection
st.markdown(
    """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Header Gradient styling */
    .header-title {
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: #8a99ad;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Premium Glassmorphism Container */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 24px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    }

    /* Custom buttons with micro-animations */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.4) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.6) !important;
    }
    div.stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Styled stats widget */
    .stat-box {
        text-align: center;
        padding: 16px;
        background: rgba(255, 255, 255, 0.015);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.03);
    }
    .stat-number {
        font-size: 2.2rem;
        font-weight: 700;
        color: #60a5fa;
        font-family: 'Outfit', sans-serif;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown('<div class="header-title">🧬 Graph-Relational AI Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Map human connections in FalkorDB and explore them using an autonomous AI Agent.</div>', unsafe_allow_html=True)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# Sidebar Database Status
with st.sidebar:
    st.markdown("### 📊 Database Diagnostics")
    
    # Get database counts
    try:
        nodes_res = db_manager.execute_query("MATCH (n:Person) RETURN count(n)")
        nodes_count = nodes_res.result_set[0][0] if nodes_res.result_set else 0
    except Exception:
        nodes_count = 0

    try:
        rels_res = db_manager.execute_query("MATCH ()-[r:RELATES_TO]->() RETURN count(r)")
        rels_count = rels_res.result_set[0][0] if rels_res.result_set else 0
    except Exception:
        rels_count = 0

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{nodes_count}</div>
            <div class="stat-label">People</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{rels_count}</div>
            <div class="stat-label">Edges</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚠️ Database Controls")
    if st.button("Clear Graph Database", help="Delete all nodes and edges"):
        db_manager.clear_graph()
        st.toast("Database cleared successfully!", icon="🗑️")
        st.rerun()

    st.markdown("---")
    st.markdown("### 💬 Chat Settings")
    if st.button("Reset Conversation History"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.toast("AI Agent conversation history reset!", icon="🧹")
        st.rerun()

# Layout: Ingestion Form (Left) & Chat Assistant (Right)
col_form, col_chat = st.columns([1, 1.2], gap="large")

with col_form:
    st.markdown("### 📥 Ingest Relationship Tuple")
    
    with st.form("relationship_form", clear_on_submit=True):
        st.markdown("**Person 1 (Source)**")
        p1_name = st.text_input("Name", key="p1_name", placeholder="e.g. Alice")
        p1_loc = st.text_input("Location", key="p1_loc", placeholder="e.g. New York")
        
        st.markdown("---")
        st.markdown("**Relationship Properties**")
        rel_type = st.selectbox(
            "Relationship Type",
            ["friend", "spouse", "boss", "employee", "sibling", "enemy", "colleague", "partner", "other"],
            index=0
        )
        sentiment = st.select_slider(
            "Emotional Sentiment",
            options=["hate", "dislike", "neutral", "like", "love"],
            value="neutral"
        )
        
        st.markdown("---")
        st.markdown("**Person 2 (Target)**")
        p2_name = st.text_input("Name", key="p2_name", placeholder="e.g. Bob")
        p2_loc = st.text_input("Location", key="p2_loc", placeholder="e.g. Los Angeles")
        
        submitted = st.form_submit_value = st.form_submit_button("Add/Update Relationship")
        
        if submitted:
            if not p1_name or not p2_name:
                st.error("Please enter both Person names.")
            else:
                try:
                    # Ingest Person nodes
                    db_manager.upsert_person(p1_name.strip(), p1_loc.strip())
                    db_manager.upsert_person(p2_name.strip(), p2_loc.strip())
                    # Ingest Directed Relationship
                    db_manager.create_relationship(p1_name.strip(), p2_name.strip(), rel_type, sentiment)
                    
                    st.success(f"Successfully recorded: {p1_name} is a {rel_type} of {p2_name} ({sentiment})")
                    # Rerun to update sidebar diagnostics
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving to database: {str(e)}")

with col_chat:
    st.markdown("### 🤖 Query Graph with AI Agent")
    st.info("Ask questions in plain English (e.g. 'Who does Alice love?' or 'Where does Bob live?').")

    # Display chat conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # AI Agent response generation
        with st.chat_message("assistant"):
            with st.spinner("AI Agent is running Cypher queries on FalkorDB..."):
                async def execute_agent():
                    config = get_agent_config()
                    # Apply conversation persistence if it exists
                    if st.session_state.conversation_id:
                        config.conversation_id = st.session_state.conversation_id
                    config.save_dir = CHATS_DIR

                    async with Agent(config=config) as agent:
                        response = await agent.chat(prompt)
                        ans = await response.text()
                        # Save the updated conversation ID
                        st.session_state.conversation_id = agent.conversation_id
                        return ans

                try:
                    # Run the async function synchronously inside Streamlit
                    agent_response = asyncio.run(execute_agent())
                    st.write(agent_response)
                    # Append assistant message
                    st.session_state.messages.append({"role": "assistant", "content": agent_response})
                except Exception as e:
                    error_msg = f"AI Agent error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
