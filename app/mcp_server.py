from fastapi import FastAPI, HTTPException
from app.tools import register_tools

app = FastAPI()

# ---------------------------------------------------
# Handlers (your business logic)
# ---------------------------------------------------
def echo_handler(text: str):
    return f"Echo: {text}"

# Map: tool_name → handler function
HANDLERS = {
    "echo": echo_handler
}

# Load tool metadata from tools.py
TOOLS = register_tools()


# ---------------------------------------------------
# Routes
# ---------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ 1) List all MCP tools
@app.get("/tools")
def list_tools():
    return [
        {
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters,
        }
        for t in TOOLS
    ]


# ✅ 2) Dynamically call any tool
@app.post("/tool/{tool_name}")
async def call_tool(tool_name: str, payload: dict):
    # Check if tool exists
    tool = next((t for t in TOOLS if t.name == tool_name), None)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    # Find handler
    handler = HANDLERS.get(tool_name)
    if not handler:
        raise HTTPException(status_code=500, detail="Handler not registered")

    # Call the handler dynamically
    try:
        result = handler(**payload)
    except TypeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameters: {str(e)}"
        )

    return {"result": result}

