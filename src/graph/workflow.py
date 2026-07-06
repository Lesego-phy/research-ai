# Connects agents, tools, and human approval

# Connects agents, tools, and human approval

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from src.models.state import ResearchState
from src.agents.researcher import research_node
from src.agents.writer import write_node
from src.agents.reviewer import reviewer_node
from src.tools.export import export_to_pdf, export_to_docx, export_to_markdown

def route_after_review(state: ResearchState) -> str:
    """
    Conditional edge: Decides whether to loop back to the writer or finish.
    """
    if state.get("is_approved_by_reviewer") or state.get("revision_count", 0) >= state.get("MAX_REVISIONS", 3):
        return "finish"
    else:
        return "revise"


def export_node(state: ResearchState) -> dict:
    """
    The Export Node: Converts the final approved text into the requested format.
    """
    print(f"📁 [Exporter] Generating {state.get('export_format', 'pdf').upper()} file...")
    draft = state.get("draft_report", "No report generated.")
    topic = state.get("user_topic", "Research_Report")
    fmt = state.get("export_format", "pdf")
    
    # Call the correct export function based on user selection
    if fmt == "pdf":
        path = export_to_pdf(draft, topic)
    elif fmt == "docx":
        path = export_to_docx(draft, topic)
    else:
        path = export_to_markdown(draft, topic)
        
    # Return the file path so it gets saved in the State
    return {"file_path": path}
# ==========================================

def build_research_graph():
    """
    Constructs and compiles the Multi-Agent Research Graph.
    """
    # 1. Initialize the Graph with our State
    workflow = StateGraph(ResearchState)

    # 2. Add the Nodes (Agents)
    workflow.add_node("research", research_node)
    workflow.add_node("write", write_node)
    workflow.add_node("review", reviewer_node)

   
    workflow.add_node("export", export_node)
    # ==========================================

    # 3. Define the Edges (The Flow)
    # Start -> Research
    workflow.set_entry_point("research")
    
    # Research -> Write
    workflow.add_edge("research", "write")
    
    # Write -> Review
    workflow.add_edge("write", "review")
    
    # Reviewer -> Conditional (Either finish or go back to Write)
    workflow.add_conditional_edges(
        "review",
        route_after_review,
        {
            # ==========================================
            #Route to "export" instead of END
            # (We don't want to end immediately, we want to generate the file first!)
            # ==========================================
            "finish": "export", 
            # ==========================================
            "revise": "write"
        }
    )

    workflow.add_edge("export", END)

    # 4. Compile the Graph

    #  memory = MemorySaver()
    
    # app = workflow.compile(
    #     checkpointer=memory, 
    #     interrupt_before=["export"] 
    # )

    #UPDATED Use SQLite for persistent memory across app restarts
    # This creates a local database file to store all conversation history.
    conn = sqlite3.connect("data/checkpoints.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)
    
    app = workflow.compile(checkpointer=memory, interrupt_before=["export"])
    return app
    

# Create a single instance of the graph to be used by the UI
research_graph = build_research_graph()