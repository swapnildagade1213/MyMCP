from fastmcp.tools import Tool

def register_tools():
    return [
        Tool(
            name="echo",
            description="Echoes the input string",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        )
    ]
