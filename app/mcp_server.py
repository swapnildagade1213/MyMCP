from fastapi import FastAPI, HTTPException
from app.tools import register_tools, ToolInfo

app = FastAPI()

# ---------------------------------------------------
# Handlers (business logic)
# ---------------------------------------------------
def echo_handler(text: str):
    return f"Echo: {text}"

def add_handler(a: float, b: float):
    return a + b

def multiply_handler(a: float, b: float):
    return a * b


# Map tool name -> handler function
HANDLERS = {
    "echo": echo_handler,
    "add": add_handler,
    "multiply": multiply_handler
}

# Load ToolInfo objects
TOOLS: list[ToolInfo] = register_tools()


# ---------------------------------------------------
# Routes
# ---------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ List all tools with metadata
@app.get("/tools")
def list_tools(include_hidden: bool = False):
    result = []
    for tinfo in TOOLS:
        if not tinfo.visible and not include_hidden:
            continue

        result.append({
            "name": tinfo.tool.name,
            "description": tinfo.tool.description,
            "parameters": tinfo.tool.parameters,
            "category": tinfo.category,
            "tags": tinfo.tags,
            "version": tinfo.version,
            "author": tinfo.author,
            "visible": tinfo.visible
        })
    return result


# ✅ Dynamic Tool Invocation
@app.post("/tool/{tool_name}")
async def call_tool(tool_name: str, payload: dict):
    tool_info = next((t for t in TOOLS if t.tool.name == tool_name), None)
    if not tool_info:
        raise HTTPException(status_code=404, detail="Tool not found")

    if not tool_info.visible:
        raise HTTPException(status_code=403, detail="Tool is hidden")

    handler = HANDLERS.get(tool_name)
    if not handler:
        raise HTTPException(status_code=500, detail="Handler not registered")

    try:
        result = handler(**payload)
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")

    return {
        "tool": tool_name,
        "category": tool_info.category,
        "result": result
    }
