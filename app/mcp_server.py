from fastapi import FastAPI, HTTPException
from app.tools import register_tools, ToolInfo
from app.executor import AsyncToolExecutor

app = FastAPI()

executor = AsyncToolExecutor()

# ---------------------------
# Handlers
# ---------------------------
async def echo_handler(text: str):
    return f"Echo: {text}"

async def add_handler(a: float, b: float):
    return a + b

async def multiply_handler(a: float, b: float):
    return a * b

executor.register("echo", echo_handler)
executor.register("add", add_handler)
executor.register("multiply", multiply_handler)

TOOLS: list[ToolInfo] = register_tools()

print("Loaded Tools:", TOOLS)   # ✅ Debug for Render logs


# ---------------------------
# ROUTES
# ---------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ ✅ GUARANTEED /tools ENDPOINT
@app.get("/tools")
def list_tools(include_hidden: bool = False):
    return [
        {
            "name": t.tool.name,
            "description": t.tool.description,
            "parameters": t.tool.parameters,
            "category": t.category,
            "tags": t.tags,
            "version": t.version,
            "author": t.author,
            "visible": t.visible
        }
        for t in TOOLS
        if t.visible or include_hidden
    ]


@app.post("/tool/{tool_name}")
async def call_tool(tool_name: str, payload: dict):
    tool_info = next((t for t in TOOLS if t.tool.name == tool_name), None)
    if not tool_info:
        raise HTTPException(status_code=404, detail="Tool not found")

    if not tool_info.visible:
        raise HTTPException(status_code=403, detail="Tool is hidden")

    try:
        result = await executor.execute(tool_name, payload)
    except TypeError as e:
        raise HTTPException(400, f"Invalid parameters: {e}")
    except ValueError as e:
        raise HTTPException(404, str(e))

    return {
        "tool": tool_name,
        "category": tool_info.category,
        "result": result
    }
