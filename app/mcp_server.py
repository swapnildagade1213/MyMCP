import logging
from typing import Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.tools import register_tools, ToolInfo
from app.executor import AsyncToolExecutor

# ---------------------------
# Logging Configuration
# ---------------------------
logger = logging.getLogger(__name__)

# ---------------------------
# Request/Response Models
# ---------------------------
class ToolExecutionRequest(BaseModel):
    """Validate tool execution payload with proper type hints."""
    params: dict[str, Any] = {}

class ToolExecutionResponse(BaseModel):
    """Standardized response format for tool execution."""
    tool: str
    category: str
    result: Any
    success: bool = True

class ToolMetadataResponse(BaseModel):
    """Standardized tool metadata response."""
    name: str
    description: str
    parameters: dict
    category: str
    tags: list[str]
    version: str
    author: str
    visible: bool

# ---------------------------
# Application Lifecycle
# ---------------------------
async def initialize_tools(executor: AsyncToolExecutor) -> None:
    """Register all built-in tool handlers."""
    executor.register("echo", echo_handler)
    executor.register("add", add_handler)
    executor.register("multiply", multiply_handler)
    logger.info("Built-in tool handlers registered")

async def startup_event() -> None:
    """App startup lifecycle event."""
    logger.info("MCP Server starting up...")
    await initialize_tools(executor)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    await startup_event()
    logger.info("✅ MCP Server initialized successfully")
    yield
    logger.info("MCP Server shutting down...")

# ---------------------------
# Tool Handlers
# ---------------------------
async def echo_handler(text: str) -> str:
    """Echo back the input text."""
    return f"Echo: {text}"

async def add_handler(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

async def multiply_handler(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

# ---------------------------
# Application Setup
# ---------------------------
executor = AsyncToolExecutor()

app = FastAPI(
    title="MCP Server",
    description="Async MCP Tool Server with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Load registered tools
TOOLS: list[ToolInfo] = register_tools()
logger.info(f"Loaded {len(TOOLS)} tools from registry")

# ---------------------------
# Helper Functions
# ---------------------------
def find_tool(tool_name: str) -> Optional[ToolInfo]:
    """Find a tool by name. Returns None if not found."""
    return next((t for t in TOOLS if t.tool.name == tool_name), None)


def build_tool_metadata(tool_info: ToolInfo) -> ToolMetadataResponse:
    """Convert ToolInfo to response model."""
    return ToolMetadataResponse(
        name=tool_info.tool.name,
        description=tool_info.tool.description,
        parameters=tool_info.tool.parameters,
        category=tool_info.category,
        tags=tool_info.tags,
        version=tool_info.version,
        author=tool_info.author,
        visible=tool_info.visible
    )

# ---------------------------
# Routes
# ---------------------------
@app.get("/", tags=["Info"])
def homepage() -> dict:
    """Homepage with available endpoints."""
    return {
        "message": "✅ MCP Server is running",
        "version": "1.0.0",
        "available_endpoints": {
            "/health": "Health check",
            "/tools": "List all available tools",
            "/tool/{name}": "Execute a specific tool"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/tools", tags=["Tools"], response_model=list[ToolMetadataResponse])
def list_tools(include_hidden: bool = False) -> list[ToolMetadataResponse]:
    """List all available tools with optional hidden tool inclusion."""
    tools = [
        build_tool_metadata(t)
        for t in TOOLS
        if t.visible or include_hidden
    ]
    logger.info(f"Retrieved {len(tools)} tools (include_hidden={include_hidden})")
    return tools

@app.post("/tool/{tool_name}", tags=["Tools"], response_model=ToolExecutionResponse)
async def call_tool(tool_name: str, request: ToolExecutionRequest) -> ToolExecutionResponse:
    """Execute a specific tool with provided parameters."""
    # Validate tool exists
    tool_info = find_tool(tool_name)
    if not tool_info:
        logger.warning(f"Tool not found: {tool_name}")
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    # Check visibility
    if not tool_info.visible:
        logger.warning(f"Attempt to access hidden tool: {tool_name}")
        raise HTTPException(status_code=403, detail="Tool is hidden")

    # Execute tool
    try:
        logger.info(f"Executing tool: {tool_name} with params: {request.params}")
        result = await executor.execute(tool_name, request.params)
        logger.info(f"Tool execution successful: {tool_name}")
    except TypeError as e:
        logger.error(f"Invalid parameters for {tool_name}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
    except ValueError as e:
        logger.error(f"Execution error for {tool_name}: {e}")
        raise HTTPException(status_code=400, detail=f"Execution error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error executing {tool_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    return ToolExecutionResponse(
        tool=tool_name,
        category=tool_info.category,
        result=result,
        success=True
    )
