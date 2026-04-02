
from fastmcp import FastMCP
from app.resources import register_resources
from app.tools import register_tools
from app.logger import log

mcp = FastMCP("fastmcp-example-server")

# Register tools
for tool in register_tools():
    mcp.add_tool(tool)

# Register resources
for resource in register_resources():
    mcp.add_resource(resource)

def run_server():
    log("Launching FastMCP server on port 8000...")
    mcp.run(
        transport="streamable-http", 
        host="0.0.0.0",
        port=8000
    )
