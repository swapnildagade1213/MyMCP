# app/mcp_server.py
import logging
from typing import Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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
# Enterprise-styled homepage returning HTML
@app.get("/", response_class=HTMLResponse, tags=["Info"])
def homepage() -> HTMLResponse:
    """Homepage with enterprise look and feel (returns HTML)."""
    html = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8"/>
      <meta name="viewport" content="width=device-width,initial-scale=1"/>
      <title>MCP Server — Dashboard</title>
      <style>
        :root{
          --bg:#0f1720; --card:#111827; --muted:#9ca3af; --accent:#2563eb;
          --success:#10b981; --surface:#0b1220; --glass:rgba(255,255,255,0.03);
          font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
        }
        html,body{height:100%;margin:0;background:linear-gradient(180deg,var(--bg),#061025);color:#e6eef8}
        .container{max-width:1100px;margin:32px auto;padding:28px}
        header{display:flex;align-items:center;justify-content:space-between;gap:16px}
        .brand{display:flex;align-items:center;gap:12px}
        .logo{width:44px;height:44px;border-radius:8px;background:linear-gradient(135deg,#0ea5e9,#7c3aed);display:flex;align-items:center;justify-content:center;font-weight:700;color:white}
        h1{margin:0;font-size:1.25rem}
        .meta{color:var(--muted);font-size:0.9rem}
        .status{padding:8px 12px;background:var(--glass);border-radius:10px;display:inline-flex;gap:8px;align-items:center}
        .status .dot{width:10px;height:10px;border-radius:50%;background:var(--success);box-shadow:0 0 8px rgba(16,185,129,0.28)}
        main{display:grid;grid-template-columns:1fr 360px;gap:20px;margin-top:22px}
        .card{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border-radius:12px;padding:18px}
        .hero{padding:28px;border-radius:12px}
        .endpoints{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:12px}
        .endpoint{padding:12px;border-radius:10px;background:rgba(255,255,255,0.02);display:flex;flex-direction:column}
        .endpoint small{color:var(--muted);margin-top:8px}
        .docs-links a{display:inline-block;margin-right:10px;padding:8px 12px;border-radius:8px;background:var(--accent);color:white;text-decoration:none}
        .tools-list{display:flex;flex-direction:column;gap:10px}
        footer{margin-top:28px;color:var(--muted);font-size:0.85rem;text-align:center}
        @media (max-width:900px){main{grid-template-columns:1fr;}.endpoints{grid-template-columns:1fr}}
      </style>
    </head>
    <body>
      <div class="container">
        <header>
          <div class="brand">
            <div class="logo">MCP</div>
            <div>
              <h1>MCP Server</h1>
              <div class="meta">Async MCP Tool Server — v1.0.0</div>
            </div>
          </div>
          <div>
            <div class="status"><span class="dot"></span><strong style="margin-left:6px">Online</strong></div>
            <div style="height:6px"></div>
            <div class="meta">Uptime: <strong>—</strong> • Environment: <strong>production</strong></div>
          </div>
        </header>

        <main>
          <section>
            <div class="card hero">
              <h2>Welcome</h2>
              <p class="meta">This dashboard provides quick access to available endpoints, tools, and API docs for the MCP Server.</p>

              <div style="margin-top:18px">
                <div style="display:flex;gap:10px;flex-wrap:wrap" class="docs-links">
                  <a href="/docs" title="Open Swagger UI">API Docs</a>
                  <a href="/redoc" title="Open ReDoc">ReDoc</a>
                  <a href="/openapi.json" title="Open OpenAPI JSON" style="background:#374151">OpenAPI JSON</a>
                  <a href="/tools" title="Browse tools" style="background:#065f46">Tool Browser</a>
                </div>
              </div>

              <h3 style="margin-top:18px">Available endpoints</h3>
              <div class="endpoints">
                <div class="endpoint">
                  <strong>GET /health</strong>
                  <small>Health check — returns service status</small>
                </div>
                <div class="endpoint">
                  <strong>GET /tools</strong>
                  <small>List registered tools and metadata</small>
                </div>
                <div class="endpoint">
                  <strong>POST /tool/{tool_name}</strong>
                  <small>Execute a tool with JSON payload {"{"} "params": {{...}} {"}"}</small>
                </div>
                <div class="endpoint">
                  <strong>GET /docs</strong>
                  <small>Interactive Swagger UI</small>
                </div>
              </div>
            </div>

            <div style="display:flex;gap:12px;margin-top:12px">
              <div class="card" style="flex:1">
                <h4>System info</h4>
                <p class="meta">Version: <strong>1.0.0</strong> • Loaded tools: <strong>{loaded}</strong></p>
                <p class="meta">Logger: <strong>{logger}</strong></p>
              </div>
              <div class="card" style="width:220px">
                <h4>Quick actions</h4>
                <div style="display:flex;flex-direction:column;gap:8px;margin-top:8px">
                  <a href="/tools" style="text-decoration:none;color:var(--accent)">Open Tool Browser →</a>
                  <a href="/docs" style="text-decoration:none;color:var(--accent)">Open API Docs →</a>
                </div>
              </div>
            </div>
          </section>

          <aside>
            <div class="card">
              <h4>Tool snapshot</h4>
              <div class="tools-list">
                <div style="padding:8px;background:rgba(255,255,255,0.01);border-radius:8px">echo — visible</div>
                <div style="padding:8px;background:rgba(255,255,255,0.01);border-radius:8px">add — visible</div>
                <div style="padding:8px;background:rgba(255,255,255,0.01);border-radius:8px">multiply — visible</div>
              </div>
            </div>

            <div class="card" style="margin-top:12px">
              <h4>Documentation</h4>
              <p class="meta">Use the links above to explore interactive docs and execute tools directly from the browser.</p>
            </div>
          </aside>
        </main>

        <footer>
          <div>© 2026 My MCP • Built for enterprise use</div>
        </footer>
      </div>
    </body>
    </html>
    """
    # Avoid calling str.format on large HTML containing literal curly braces used by CSS.
    # Replace only the intended placeholders.
    html = html.replace("{loaded}", str(len(TOOLS))).replace("{logger}", logger.name if logger else "mcp_server")
    return HTMLResponse(content=html, status_code=200)

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
