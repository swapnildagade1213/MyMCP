from fastmcp.tools import Tool

def echo_handler(text: str):
    return f"Echo: {text}"

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
            },
            handler=echo_handler
        )
    ]
