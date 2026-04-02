from fastapi import FastAPI
from fastapi import HTTPException
from app.tools import register_tools

app = FastAPI()

# ---------------------------------------------
# Handlers for tools (business logic)
# ---------------------------------------------
def echo_handler(text: str):
    return f"Echo: {text}"

# Map tool name → handler function
HANDLERS = {
    "echo": echo_handler
}

# ---------------------------------------------
# Register tools as HTTP endpoints
# ---------------------------------------------
TOOLS = register_tools()

@app.get("/health")
def health():
    return {"status": "ok"}

# For each tool, make a POST endpoint:
for tool in TOOLS:
    route = f"/tools/{tool.name}"

    async def dynamic_tool_endpoint(payload: dict, t=tool):
        handler = HANDLERS.get(t.name)
        if not handler:
            raise HTTPException(status_code=404, detail="Handler not found")

        # extract params dynamically
        try:
            result = handler(**payload)
        except TypeError:
            raise HTTPException(status_code=400, detail="Invalid input schema")

        return {"result": result}

    # Dynamically add the route
    app.post(route)(dynamic_tool_endpoint)
