from fastmcp.tools import Tool
from pydantic import BaseModel
from typing import List, Optional


class ToolInfo(BaseModel):
    tool: Tool
    category: str
    tags: Optional[List[str]] = []
    version: Optional[str] = "1.0"
    author: Optional[str] = "system"
    visible: bool = True


def register_tools():
    return [
        # -------------------------
        # Tool 1: echo
        # -------------------------
        ToolInfo(
            tool=Tool(
                name="echo",
                description="Echoes the input string",
                parameters={
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"]
                }
            ),
            category="utility",
            tags=["echo", "text"],
            version="1.0",
            author="your-name",
            visible=True
        ),

        # -------------------------
        # Tool 2: add
        # -------------------------
        ToolInfo(
            tool=Tool(
                name="add",
                description="Adds two numbers",
                parameters={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            ),
            category="math",
            tags=["addition", "math"],
            version="1.0",
            author="your-name",
            visible=True
        ),

        # -------------------------
        # Tool 3: multiply
        # -------------------------
        ToolInfo(
            tool=Tool(
                name="multiply",
                description="Multiplies two numbers",
                parameters={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            ),
            category="math",
            tags=["multiplication", "math"],
            version="1.0",
            author="your-name",
            visible=True
        )
    ]
