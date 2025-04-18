import chainlit as cl

from llama_index.core.agent import FunctionCallingAgent
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

from mcp import ClientSession
from mcp.types import CallToolResult, TextContent

llm = Ollama(model="qwen2.5", temperature=0)
mcp_tools_cache = {}

@cl.on_chat_start
async def start():
    cl.user_session.set(
        "agent",
        SimpleChatEngine.from_defaults(
            llm=llm,
        )
    )
    memory = ChatMemoryBuffer.from_defaults()
    memory.put(
        ChatMessage(
            role="system", 
            content="You are a helpful AI assistant. You can access tools using MCP servers if available."
        )
    )
    cl.user_session.set(
        "memory",
        memory,
    )

@cl.on_mcp_connect
async def on_mcp_connect(
    connection, 
    session: ClientSession
):
    
    try:
        mcp_client = BasicMCPClient(connection.url)
        mcp_tool_spec = McpToolSpec(client=mcp_client)
        tools = await mcp_tool_spec.to_tool_list_asnyc()
        agent = cl.user_session.get("agent")
        if isinstance(agent, SimpleChatEngine):
            agent = FunctionCallingAgent.from_tools(
                llm = llm,
                tools = tools
            )
        else: #update tool list
            ...
        cl.user_session.set("agent", agent)
        await cl.Message(f"Connected to MCP server: {connection.name} on {connection.url}").send()
    
        result = await session.list_tools()

        tools = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in result.tools
        ]

        mcp_tools_cache[connection.name] = tools

        mcp_tools = cl.user_session.get("mcp_tools", {})
        mcp_tools[connection.name] = tools
        cl.user_session.set("mcp_tools", mcp_tools)

        await cl.Message(
            f"Found {len(tools)} tools from {connection.name} MCP server."
        ).send()
    except Exception as e:
        await cl.Message(f"Error listing tools from MCP server: {str(e)}").send()

@cl.on_mcp_disconnect
async def on_mcp_disconnect(name: str, session: ClientSession):
    if name in mcp_tools_cache:
        del mcp_tools_cache[name]

    mcp_tools = cl.user_session.get("mcp_tools", {})
    if name in mcp_tools:
        del mcp_tools[name]
        cl.user_session.set("mcp_tools", mcp_tools)

    await cl.Message(f"Disconnected from MCP server: {name}").send()