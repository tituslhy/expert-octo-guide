# Welcome to a mini exploration of Model Context Protocols
This little GitHub repository introduces the features of model context protocols (MCP), implementing MCP integrations with Chainlit and LlamaIndex.

<p align="center">
    <img src="./images/mcp_banner.png">
</p>

## Notes
In this repository I use a local LLM deployed on Ollama!

### To install requirements
```pip install -r requirements.txt```

### To spin up the chainlit applications
Note that I've set the port to 8001 because Chainlit's default port is 8000 which conflicts with the MCP endpoint deployment (that default port is also 8000).
```chainlit run app_llamaindex.py --port 8001```

### To spin up the mcp endpoint
```uv run tools_main.py --server_type=sse```

## Repository Layout
```
.
|-  .chainlit                       <- Chainlit configuration files
|-  controllers 
|   |- api.py                       <- Simple FastAPI implementation endpoints
|-  docs                            <- Contains Paul Graham's essay to be used by MCP endpoints
|-  notebooks
|    |- test_fastapi_fastmcp.ipynb  <- Short notebook showing API and MCP interactions.
|    |- test_tools_main.ipynb       <- The main notebook testing mcp deployments
|-  protocols
|   |- stock_tools.py               <- MCP for stock tools
|   |- weather_tools.py             <- MCP for weather tools (from FastAPI)
|   |- writing_tools.py             <- MCP for llm writing tools
|-  src                             <- Utility functions 
|-  app_llamaindex.py               <- Sample chainlit implementation using LlamaIndex
|-  app_openai.py                   <- Sample chainlit implementation using OpenAI SDK
|-  tools_main.py                   <- Main MCP protocol file
```