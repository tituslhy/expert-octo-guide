from fastmcp import FastMCP
from mcp.stock_tools import mcp as stock_mcp
from mcp.writing_tools import mcp as writing_mcp
from mcp.weather_tools import mcp as weather_mcp

mcp = FastMCP("Writing and stock analysis tools")

mcp.mount(
    "stock_tools", stock_mcp,
    "writing_tools", writing_mcp,
    "weather_tools", weather_mcp
)

@mcp.tool()
def ping(): 
    return "MCP compose OK"

if __name__ == "__main__":
    mcp.run(transport="sse")