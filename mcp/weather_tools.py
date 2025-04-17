import os
import sys
from fastmcp import FastMCP

__curdir__ = os.getcwd()
if "mcp" in __curdir__:
    sys.path.append("../controllers")
else:
    sys.path.append("./controllers")

from api import fastapi_app

mcp = FastMCP.from_fastapi(fastapi_app, port=3000)

if __name__ == "__main__":
    mcp.run(transport="sse")