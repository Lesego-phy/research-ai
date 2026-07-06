# Integration tests for the graph

"""Integration tests for the full workflow."""
import pytest
from src.graph.workflow import build_research_graph

def test_graph_compiles():
    """Test that the graph compiles without errors."""
    graph = build_research_graph()
    assert graph is not None

def test_graph_has_all_nodes():
    """Test that the graph has all required nodes."""
    graph = build_research_graph()
    
    # Get the graph structure
    nodes = list(graph.nodes.keys())
    
    assert "research" in nodes
    assert "write" in nodes
    assert "review" in nodes
    assert "export" in nodes

@pytest.mark.asyncio
async def test_full_workflow():
    """Test the complete research workflow end-to-end."""
    graph = build_research_graph()
    
    initial_state = {
        "messages": [],
        "user_topic": "test topic",
        "scraped_documents": [],
        "search_queries": [],
        "draft_report": None,
        "reviewer_feedback": None,
        "is_approved_by_reviewer": False,
        "revision_count": 0,
        "MAX_REVISIONS": 1,  # Keep low for testing
        "is_approved_by_human": False,
        "export_format": "md",
        "file_path": None,
        "rag_context": "",
        "academic_context": ""
    }
    
    config = {"configurable": {"thread_id": "test_thread"}}
    
    # Run the graph (it will pause at export due to interrupt_before)
    result = await graph.ainvoke(initial_state, config)
    
    # Verify the graph ran through the expected nodes
    assert result["draft_report"] is not None
    assert len(result["draft_report"]) > 100
    assert result["revision_count"] >= 1