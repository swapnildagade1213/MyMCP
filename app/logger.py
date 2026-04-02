import datetime, os
LOG_FILE = os.path.expanduser("~/fastmcp-server/logs/server.log")

def log(msg:str):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {msg}
")
