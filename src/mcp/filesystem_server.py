"""
MCP Server that provides file system access to agents.
This allows agents to read files from a specific directory.
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import os
import json

# Directory that agents are allowed to access
ALLOWED_DIR = os.path.abspath("data/knowledge_base")
os.makedirs(ALLOWED_DIR, exist_ok=True)

app = Server("filesystem-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="read_file",
            description="Read the contents of a file from the knowledge base directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to read (e.g., 'report.txt')"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="list_files",
            description="List all files in the knowledge base directory",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "read_file":
        filename = arguments["filename"]
        filepath = os.path.join(ALLOWED_DIR, filename)
        
        # Security check: ensure file is within allowed directory
        if not os.path.abspath(filepath).startswith(ALLOWED_DIR):
            return [TextContent(type="text", text="Error: Access denied")]
        
        if not os.path.exists(filepath):
            return [TextContent(type="text", text=f"Error: File '{filename}' not found")]
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading file: {str(e)}")]
    
    elif name == "list_files":
        files = os.listdir(ALLOWED_DIR)
        return [TextContent(type="text", text=json.dumps(files))]
    
    return [TextContent(type="text", text="Unknown tool")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())