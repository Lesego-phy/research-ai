# Finds and scrapes info

from src.agents.llm import azure_llm
from src.tools.search import tavily_search
from src.tools.scrape import scrape_urls
from src.tools.rag import query_uploaded_documents
from src.guardrails.validators import search_rate_limiter
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import re


#Async helper to query OpenAlex MCP

async def query_openalex_mcp(topic: str) -> str:
    """Queries the OpenAlex MCP server for academic papers."""
    try:
        async with MultiServerMCPClient({
            "openalex": {
                "command": "python",
                "args": [os.path.join(os.path.dirname(__file__), "..", "mcp", "openalex_server.py")],
            }
        }) as client:
            tools = client.get_tools()
            search_tool = next((t for t in tools if t.name == "search_works"), None)
            
            if not search_tool:
                return ""
            
            # Search for recent academic papers on the topic
            result = await search_tool.ainvoke({
                "query": topic,
                "limit": 5,
                "year": 2020  # Focus on recent research
            })
            return result
    except Exception as e:
        print(f"[OpenAlex MCP] Error: {e}")
        return ""


def research_node(state: dict) -> dict:
    """
    The Researcher Node: Generates queries, searches the web, and scrapes content.
    """
    user_topic = state["user_topic"]
    print(f"🔍 [Researcher] Starting research on: {user_topic}")

    # Reset rate limiter at the start of each research run
    search_rate_limiter.reset()

    # 1. Use LLM to generate specific search queries
    prompt = f"Given the research topic '{user_topic}', generate exactly 3 highly specific search queries to find the most relevant, recent, and reliable information. Return ONLY a comma-separated list of the 3 queries, nothing else."
    
    response = azure_llm.invoke(prompt)
    queries = [q.strip() for q in response.content.split(',')]
    
    # 2. Search Tavily for each query
    all_urls = set()
    search_results_text = []

     for query in queries:
        # Checks rate limit before searching
        if not search_rate_limiter.can_call():
            print("[Researcher] Rate limit reached. Stopping searches.")
            break
            
        print(f"   🔎 Web Searching: {query}")
        results = tavily_search.invoke(query)
        search_results_text.append(f"Query: {query}\n{results}")
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', results)
        all_urls.update(urls)

    
    # for query in queries:
    #     print(f"   🔎 Searching: {query}")
    #     results = tavily_search.invoke(query)
    #     search_results_text.append(f"Query: {query}\n{results}")
        
    #     # Extract URLs for scraping
    #     # Note: TavilySearchResults returns a string, so we parse it or use the native tool if we need raw URLs.
    #     # To make scraping easier, let's just use the native Tavily client here to get raw URLs, 
    #     # OR we can just pass the search results text to the writer. 
    #     # For deep scraping, let's extract URLs from the string (simplified approach):
    #     import re
    #     urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', results)
    #     all_urls.update(urls)

    # # 3. Scrape the top 5 unique URLs
    # urls_to_scrape = list(all_urls)[:5]
    # print(f"   🕸️ [Researcher] Scraping {len(urls_to_scrape)} URLs...")
    
    # scraped_docs = []
    # if urls_to_scrape:
    #     scraped_docs = scrape_urls.invoke({"urls": urls_to_scrape})

     # 3. Scrape URLs
    urls_to_scrape = list(all_urls)[:5]
    print(f"   🕸️ [Researcher] Scraping {len(urls_to_scrape)} URLs...")
    scraped_docs = scrape_urls.invoke({"urls": urls_to_scrape}) if urls_to_scrape else []

    #Query the Vector DB (RAG) for uploaded documents
    print(" [Researcher] Checking uploaded documents (RAG)...")
    # I use the user_topic as the initial query for the RAG tool
    rag_context = query_uploaded_documents.invoke(user_topic)

    # Query OpenAlex MCP (academic papers)
    print("[Researcher] Searching academic papers via OpenAlex MCP...")
    try:
        academic_context = asyncio.run(query_openalex_mcp(user_topic))
    except Exception as e:
        print(f"OpenAlex query failed: {e}")
        academic_context = ""
    
    # Combine web and RAG context for the Writer
    combined_context = "\n\n--- WEB RESEARCH ---\n\n".join(search_results_text)
    if "No documents have been uploaded" not in rag_context and "No relevant information" not in rag_context:
        combined_context += f"\n\n--- UPLOADED DOCUMENTS (RAG) ---\n\n{rag_context}"

    # Add academic context
    if academic_context and "No academic papers" not in academic_context:
        combined_context += f"\n\n--- ACADEMIC PAPERS (OpenAlex) ---\n\n{academic_context}"

        # Query MCP filesystem server
    print(" [Researcher] Checking knowledge base via MCP...")
    
    async def query_mcp():
        async with MultiServerMCPClient({
            "filesystem": {
                "command": "python",
                "args": ["src/mcp/filesystem_server.py"],
            }
        }) as client:
            # List available files
            list_tool = client.get_tools("filesystem")[1]  # list_files tool
            files = await list_tool.ainvoke({})
            
            # Read relevant files (simplified - you could make this smarter)
            mcp_context = ""
            if files and files != "[]":
                read_tool = client.get_tools("filesystem")[0]  # read_file tool
                # For now, just read the first file as an example
                # In production, you'd search for relevant files
                file_list = json.loads(files)
                if file_list:
                    content = await read_tool.ainvoke({"filename": file_list[0]})
                    mcp_context = f"From knowledge base:\n{content}"
            
            return mcp_context
    
    # Run async MCP query
    try:
        mcp_context = asyncio.run(query_mcp())
        if mcp_context:
            combined_context += f"\n\n--- KNOWLEDGE BASE (MCP) ---\n\n{mcp_context}"
    except Exception as e:
        print(f"MCP query failed: {e}")
        mcp_context = ""

    # 4. Update the State
    return {
        "search_queries": queries,
        "scraped_documents": scraped_docs,
        "rag_context": rag_context, # Save to state
        "academic_context": academic_context,
        "messages": [HumanMessage(content=f"Research completed for {user_topic}. Found {len(scraped_docs)} documents.")]
    }