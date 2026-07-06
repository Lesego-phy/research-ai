# Tavily Search Tool

from langchain_community.tools.tavily_search import TavilySearchResults
from src.config import settings

def get_search_tool() -> TavilySearchResults:
    """
    Initializes and returns the Tavily Search Tool.
    """
    # We limit to 5 results to keep context windows manageable and reduce costs
    tool = TavilySearchResults(
        max_results=5,
        search_depth="advanced", # 'advanced' takes longer but gets deeper content
        include_answer=True,     # Tavily will also generate a quick summary
        include_raw_content=False # We will scrape the raw content ourselves for better control
    )
    return tool

# Create a single instance to be used by our agents
tavily_search = get_search_tool()