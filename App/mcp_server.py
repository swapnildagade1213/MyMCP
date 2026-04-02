from fastmcp import FastMCP
from app.resources import register_resources
from app.tools import register_tools
from app.logger import log

app = FastMCP(name="fastmcp-example-server")

@app.on_startup
async def startup():
    log("FastMCP Starting...")
    for r in register_resources(): app.add_resource(r)
    for t in register_tools(): app.add_tool(t)

def run_server():
    import uvicorn
    log("Launching Uvicorn MCP server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
