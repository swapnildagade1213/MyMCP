from fastapi import FastAPI, HTTPException
from app.tools import register_tools, ToolInfo
from app.executor import AsyncToolExecutor

app = FastAPI()
executor = AsyncToolExecutor()

# ---------------------------
# Register handlers
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

# ---------------------------
# Routes
# ---------------------------
@app.post("/tool/{tool_name}")
async def call_tool(tool_name: str, payload: dict):
    tool = next((t for t in TOOLS if t.tool.name == tool_name), None)
    if not tool:
        raise HTTPException(404, "Tool not found")

    if not tool.visible:
        raise HTTPException(403, "Tool is hidden")

    try:
        result = await executor.execute(tool_name, payload)
    except TypeError as e:
        raise HTTPException(400, f"Invalid parameters: {e}")
    except ValueError as e:
        raise HTTPException(404, str(e))

    return {
        "tool": tool_name,
        "category": tool.category,
        "result": result
    }
