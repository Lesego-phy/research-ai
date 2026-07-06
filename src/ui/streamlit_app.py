import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import streamlit as st
from src.graph.workflow import research_graph
from src.tools.rag import ingest_pdf
from src.guardrails.validators import validate_input, validate_output

# Ensuring data directories exist
os.makedirs("data/uploads", exist_ok=True)

#Page Config
st.set_page_config(page_title="AI-Powered Research", page_icon="🔍", layout="wide")

# Session State Initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "user_session_1"
if "graph_config" not in st.session_state:
    st.session_state.graph_config = {"configurable": {"thread_id": st.session_state.thread_id}}
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "show_approval" not in st.session_state:
    st.session_state.show_approval = False

#UI Layout
st.title("🔍 AI-Powered Research System")
st.markdown("Enter a topic, and let our AI agents research, write, and fact-check a report for you.")

#Sidebar for Settings
with st.sidebar:
    st.header("⚙️ Settings")
    export_format = st.selectbox("Export Format", ["pdf", "docx", "md"], index=0)
    
    # if st.button("🔄 Reset Conversation"):
    #     # Reset session state to start fresh
    #     for key in list(st.session_state.keys()):
    #         del st.session_state[key]
    #     st.rerun()

         #   RAG File Uploader
    st.header("📚 Document Knowledge Base (RAG)")
    uploaded_file = st.file_uploader("Upload a PDF for the AI to read", type=["pdf"])
    
    if uploaded_file is not None:
        # Save file locally
        file_path = os.path.join("data/uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Ingest into Vector DB
        with st.spinner("Processing PDF into Vector Database..."):
            ingest_pdf(file_path)
        st.success(f"✅ '{uploaded_file.name}' is now in the AI's memory!")

    st.divider()
    if st.button("🔄 Reset Conversation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main Chat/Execution Area
user_topic = st.chat_input("Enter your research topic (e.g., 'Is AI bounded by Laws of Physics from Quantum Computing')")

if user_topic and not st.session_state.is_running:
    
    # INPUT GUARDRAIL: Validate the user's topic
    is_valid, error_msg = validate_input(user_topic)
    if not is_valid:
        st.error(f"🚫 {error_msg}")
        st.stop() # Stops the Streamlit script here so the graph doesn't run

    # Only set these flags if the input passed the guardrail!
    st.session_state.is_running = True
    st.session_state.show_approval = False
    
    with st.spinner("🚀 Agents are researching, writing, and reviewing... Please wait."):
        # 1. Define Initial State
        initial_state = {
            "messages": [],
            "user_topic": user_topic,
            "scraped_documents": [],
            "search_queries": [],
            "draft_report": None,
            "reviewer_feedback": None,
            "is_approved_by_reviewer": False,
            "revision_count": 0,
            "MAX_REVISIONS": 2,
            "is_approved_by_human": False,
            "export_format": export_format,
            "file_path": None
        }
        
        # 2. Invoke Graph (It will pause at the 'export' node)
        final_state = research_graph.invoke(initial_state, st.session_state.graph_config)
        
        # 3. Show the draft for approval
        st.session_state.draft_report = final_state.get("draft_report")
        st.session_state.show_approval = True
        st.session_state.is_running = False
        st.rerun()

#   Display Draft & Approval Buttons
if st.session_state.show_approval:
    st.subheader("📝 Draft Report for Review")
    st.markdown(st.session_state.draft_report)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve & Export", type="primary"):
            st.session_state.is_running = True
            # Update state to indicate human approval
            research_graph.update_state(
                st.session_state.graph_config, 
                {"is_approved_by_human": True}
            )
            # Resume the graph (it will now run the export node)
            final_state = research_graph.invoke(None, st.session_state.graph_config)
            
            st.session_state.file_path = final_state.get("file_path")
            st.session_state.show_approval = False
            st.session_state.is_running = False
            st.rerun()
            
    with col2:
        if st.button("❌ Reject & Regenerate"):
            st.session_state.is_running = True
            # Update state to force a rewrite
            research_graph.update_state(
                st.session_state.graph_config, 
                {"is_approved_by_human": False, "critic_feedback": "Human rejected the draft. Please rewrite with more detail."}
            )
            # We need to route it back to write. For simplicity in this UI, 
            # we'll just clear the draft and re-invoke from the beginning or write node.
            # Let's just reset the approval and tell the user to refresh.
            st.warning("Rejected! Please refresh the page to start a new research run with new parameters.")
            st.session_state.show_approval = False
            st.session_state.is_running = False
            st.rerun()

#     Display Final Exported File 
if "file_path" in st.session_state and st.session_state.file_path:
    st.success("✅ Report successfully generated and exported!")
    
    file_path = st.session_state.file_path
    file_name = os.path.basename(file_path)
    
    with open(file_path, "rb") as file:
        st.download_button(
            label=f"📥 Download {file_name}",
            data=file,
            file_name=file_name,
            mime="application/octet-stream"
        )