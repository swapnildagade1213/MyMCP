from fastmcp import Tool

def register_tools():
    return [Tool(name="echo", description="Echoes the input string", input_schema={"type": "object", "properties": {"text": {"type": "string"}}}, func=lambda text: f"Echo: {text}")]
