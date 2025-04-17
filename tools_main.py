from fastmcp import FastMCP
from protocols.stock_tools import mcp as stock_mcp
from protocols.writing_tools import mcp as writing_mcp
from protocols.weather_tools import mcp as weather_mcp

mcp = FastMCP("Writing and stock analysis tools")

mcp.mount("stock_tools", stock_mcp)
mcp.mount("writing_tools", writing_mcp)
mcp.mount("weather_tools", weather_mcp)

@mcp.tool()
def ping(): 
    return "MCP compose OK"

if __name__ == "__main__":
    mcp.run(transport="sse")