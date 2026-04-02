from fastmcp.resources import Resource

def register_resources():
    return [Resource(uri="resource://hello", mimeType="text/plain", get=lambda: "Hello from FastMCP on PythonAnywhere!")]
