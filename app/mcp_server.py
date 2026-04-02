from app.tools import register_tools

def echo_handler(text: str):
    return f"Echo: {text}"

class MCPServer:
    def __init__(self):
        self.handlers = {}

    def add_tool(self, name, func):
        self.handlers[name] = func

    def run(self):
        print("Server ready")

server = MCPServer()

# Register all tools + their handlers
server.add_tool("echo", echo_handler)

def run_server():
    server.run()
