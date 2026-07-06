from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from rich import print
import os
from dotenv import load_dotenv
load_dotenv()

# Test if all the graphhs work and are connected with the Azure LLM, on the terminal
# test_graph.py
from src.graph.workflow import research_graph

# Define the initial state
initial_state = {
    "messages": [],
    "user_topic": "The impact of artificial intelligence on modern healthcare in 2026",
    "scraped_documents": [],
    "search_queries": [],
    "draft_report": None,
    "critic_feedback": None,
    "is_approved_by_critic": False,
    "revision_count": 0,
    "MAX_REVISIONS": 2, # Keep it low for testing to save API costs
}

print("🚀 Starting the Research Pipeline...")
final_state = research_graph.invoke(initial_state)

print("\n" + "="*50)
print("✅ FINAL APPROVED REPORT:")
print("="*50)
print(final_state["draft_report"])