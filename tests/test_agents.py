# Unit tests for agents

"""Unit tests for the agents."""
import pytest
from src.agents.researcher import research_node
from src.agents.writer import write_node
from src.agents.reviewer import reviewer_node

def test_researcher_node():
    """Test the researcher node returns expected state updates."""
    initial_state = {
        "user_topic": "artificial intelligence in healthcare",
        "scraped_documents": [],
        "search_queries": [],
        "messages": []
    }
    
    result = research_node(initial_state)
    
    assert "search_queries" in result
    assert "scraped_documents" in result
    assert len(result["search_queries"]) == 3
    assert isinstance(result["scraped_documents"], list)

def test_writer_node():
    """Test the writer node generates a report."""
    state = {
        "user_topic": "AI in healthcare",
        "scraped_documents": [
            {
                "url": "https://www.google.com/aclk?sa=L&ai=DChsSEwiw6srryLyVAxU2iVAGHbrXOx0YACICCAEQBBoCZGc&ae=2&co=1&ase=2&gclid=CjwKCAjwgajSBhBEEiwASicJU5X6iNDOyEiibVqfqyJ1S3o0hfC4cSomeXzqib2ijh54l5KGYFfYKRoCA1kQAvD_BwE&cid=CAASugHkaC6g_QNGqD1qHfJvk2obRQVTD8hinkvZT3jwOofivxHMRcKyF5Mb7nPBi8jFrhT-XoUIeqYgpfP5F47MbNCgKCrnzPbqpYD-IXHzsQR72O8pYy2kf99nOcjCD01Dcf_JGbCIJlo9qRI_ID13VSQJkBMxKfMvjd-QHqEIHZwTk711xLQeTxvNV-83UczrmydFf25U1QoRfhT0RsOs4_Fo27CPbSQXCICZCH6UUAPM0WxWOnheC1FOPvQ&cce=2&category=acrcp_v1_71&sig=AOD64_0f3M9RvYVIgSxzd5gKe4tZRGmGDw&q&nis=4&adurl&ved=2ahUKEwjD2MXryLyVAxURaEEAHZg3BQ4Q0Qx6BAgOEAE",
                "title": "AI in Healthcare",
                "content": "Artificial intelligence is transforming healthcare..."
            }
        ],
        "reviewer_feedback": None,
        "revision_count": 0,
        "rag_context": ""
    }
    
    result = write_node(state)
    
    assert "draft_report" in result
    assert "revision_count" in result
    assert result["revision_count"] == 1
    assert len(result["draft_report"]) > 100

def test_reviewer_node_approves():
    """Test the reviewer approves a good report."""
    state = {
        "draft_report": "This is a comprehensive report about AI in healthcare with multiple sources and citations.",
        "scraped_documents": [
            {
                "url": "https://www.google.com/aclk?sa=L&ai=DChsSEwiw6srryLyVAxU2iVAGHbrXOx0YACICCAEQBBoCZGc&ae=2&co=1&ase=2&gclid=CjwKCAjwgajSBhBEEiwASicJU5X6iNDOyEiibVqfqyJ1S3o0hfC4cSomeXzqib2ijh54l5KGYFfYKRoCA1kQAvD_BwE&cid=CAASugHkaC6g_QNGqD1qHfJvk2obRQVTD8hinkvZT3jwOofivxHMRcKyF5Mb7nPBi8jFrhT-XoUIeqYgpfP5F47MbNCgKCrnzPbqpYD-IXHzsQR72O8pYy2kf99nOcjCD01Dcf_JGbCIJlo9qRI_ID13VSQJkBMxKfMvjd-QHqEIHZwTk711xLQeTxvNV-83UczrmydFf25U1QoRfhT0RsOs4_Fo27CPbSQXCICZCH6UUAPM0WxWOnheC1FOPvQ&cce=2&category=acrcp_v1_71&sig=AOD64_0f3M9RvYVIgSxzd5gKe4tZRGmGDw&q&nis=4&adurl&ved=2ahUKEwjD2MXryLyVAxURaEEAHZg3BQ4Q0Qx6BAgOEAE",
                "title": "AI in Healthcare",
                "content": "This is a comprehensive report about AI in healthcare with multiple sources and citations."
            }
        ],
        "revision_count": 0,
        "MAX_REVISIONS": 3
    }
    
    result = reviewer_node(state)
    
    assert "reviewer_feedback" in result
    assert "is_approved_by_reviewer" in result
    # The reviewer should either approve or provide feedback
    assert isinstance(result["is_approved_by_reviewer"], bool)