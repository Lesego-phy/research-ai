
"""
MCP Server that provides access to OpenAlex - a free, open catalog of 
250+ million academic papers, authors, and institutions.
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import requests
import json

# OpenAlex API base URL
OPENALEX_API = "https://api.openalex.org"

POLITE_EMAIL = "innocentmatsepe01@gmail.com"
HEADERS = {"MATSEPE": POLITE_EMAIL}

app = Server("openalex-server")

# Helper: Format a work (paper) for the LLM
def format_work(work: dict) -> str:
    """Formats an OpenAlex work into readable text."""
    title = work.get("title", "No title")
    doi = work.get("doi", "No DOI")
    year = work.get("publication_year", "Unknown")
    
    # Extract authors
    authors = []
    for authorship in work.get("authorships", [])[:5]:  # Limit to 5 authors
        name = authorship.get("author", {}).get("display_name", "Unknown")
        authors.append(name)
    authors_str = ", ".join(authors) if authors else "Unknown authors"
    
    # Extract abstract (OpenAlex stores it as an inverted index)
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    
    # Citation count
    citations = work.get("cited_by_count", 0)
    
    # Source (journal)
    source = work.get("primary_location", {}).get("source", {}).get("display_name", "Unknown journal")
    
    return f"""
Title: {title}
Authors: {authors_str}
Year: {year}
Journal: {source}
DOI: {doi}
Citations: {citations}
Abstract: {abstract or "No abstract available"}
"""

def reconstruct_abstract(inverted_index):
    """OpenAlex stores abstracts as inverted indexes - this reconstructs them."""
    if not inverted_index:
        return None
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(word for _, word in word_positions)

# Define the MCP Tools

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_works",
            description="Search for academic papers by keyword. Returns titles, authors, abstracts, and citation counts. Use this to find peer-reviewed research on a topic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keywords (e.g., 'transformer neural networks', 'climate change mitigation')"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Optional: filter to papers published in this year or later"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return (default 5, max 20)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_work_details",
            description="Get full details for a specific academic paper using its OpenAlex ID or DOI.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_id": {
                        "type": "string",
                        "description": "OpenAlex ID (e.g., 'W2741809807') or DOI (e.g., '10.1038/nature12373')"
                    }
                },
                "required": ["work_id"]
            }
        ),
        Tool(
            name="search_authors",
            description="Search for researchers/authors by name or affiliation. Useful to find experts in a field.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Author name or institution (e.g., 'Yann LeCun', 'MIT')"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_citations",
            description="Find papers that cite a specific work. Useful for tracing research influence.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_id": {
                        "type": "string",
                        "description": "OpenAlex ID of the paper to find citations for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of citing papers to return (default 5)"
                    }
                },
                "required": ["work_id"]
            }
        )
    ]

# Implement the Tool Logic

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "search_works":
            query = arguments["query"]
            year = arguments.get("year")
            limit = min(arguments.get("limit", 5), 20)
            
            # Build the API URL
            url = f"{OPENALEX_API}/works"
            params = {
                "search": query,
                "per-page": limit,
                "sort": "cited_by_count:desc"  # Most cited first
            }
            if year:
                params["filter"] = f"from_publication_date:{year}-01-01"
            
            response = requests.get(url, params=params, headers=HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            works = data.get("results", [])
            if not works:
                return [TextContent(type="text", text=f"No academic papers found for '{query}'.")]
            
            formatted = [format_work(w) for w in works]
            result_text = f"Found {len(works)} academic papers for '{query}':\n\n" + "\n---\n".join(formatted)
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_work_details":
            work_id = arguments["work_id"]
            
            # Handle DOI vs OpenAlex ID
            if work_id.startswith("10."):
                work_id = f"doi:{work_id}"
            elif not work_id.startswith("W") and not work_id.startswith("https"):
                work_id = f"W{work_id}"
            
            url = f"{OPENALEX_API}/works/{work_id}"
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            work = response.json()
            
            return [TextContent(type="text", text=format_work(work))]
        
        elif name == "search_authors":
            query = arguments["query"]
            url = f"{OPENALEX_API}/authors"
            params = {"search": query, "per-page": 5}
            
            response = requests.get(url, params=params, headers=HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            authors = data.get("results", [])
            if not authors:
                return [TextContent(type="text", text=f"No authors found for '{query}'.")]
            
            formatted = []
            for a in authors:
                formatted.append(f"""
Name: {a.get('display_name')}
ID: {a.get('id')}
Works: {a.get('works_count', 0)}
Citations: {a.get('cited_by_count', 0)}
Affiliations: {', '.join([inst.get('institution', {}).get('display_name', '') for inst in a.get('affiliations', [])[:3]])}
""")
            return [TextContent(type="text", text="\n---\n".join(formatted))]
        
        elif name == "get_citations":
            work_id = arguments["work_id"]
            limit = min(arguments.get("limit", 5), 20)
            
            if not work_id.startswith("https"):
                work_id = f"https://openalex.org/{work_id}"
            
            url = f"{OPENALEX_API}/works"
            params = {
                "filter": f"cites:{work_id}",
                "per-page": limit,
                "sort": "cited_by_count:desc"
            }
            
            response = requests.get(url, params=params, headers=HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            works = data.get("results", [])
            if not works:
                return [TextContent(type="text", text="No papers found that cite this work.")]
            
            formatted = [format_work(w) for w in works]
            return [TextContent(type="text", text=f"Papers citing this work:\n\n" + "\n---\n".join(formatted))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except requests.exceptions.RequestException as e:
        return [TextContent(type="text", text=f"OpenAlex API error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

# Server Entry Point

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())