import chainlit as cl

from llama_index.core.agent import FunctionCallingAgent
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

llm = Ollama(model="qwen2.5", temperature=0)

@cl.on_chat_start
async def start():
    """Handler for chat start events. Sets session variables."""
    
    cl.user_session.set(
        "mcp_tools", {}
    )
    cl.user_session.set(
        "agent",
        SimpleChatEngine.from_defaults(
            llm=llm,
        )
    )
    memory = ChatMemoryBuffer.from_defaults()
    memory.put(
        ChatMessage(
            role=MessageRole.SYSTEM, 
            content="You are a helpful AI assistant. You can access tools using MCP servers if available."
        )
    )
    cl.user_session.set(
        "memory",
        memory,
    )

@cl.on_message
async def on_message(message: cl.Message):
    """Handler for message received events. Pings llm agent."""
    
    response = await llm_agent(message)
    await cl.Message(content=response).send()

@cl.step(type="llm")
async def llm_agent(message: cl.Message):
    """Handler for LLM agent operations."""
    
    memory = cl.user_session.get("memory")
    # Retrieve the chat history
    chat_history = memory.get()
    agent = cl.user_session.get("agent")
    response = await agent.achat(message.content, chat_history=chat_history)
    memory.put(
        ChatMessage(
            role=MessageRole.USER,
            content=message.content,
        )
    )
    memory.put(
        ChatMessage(
            role=MessageRole.ASSISTANT,
            content=str(response),
        )
    )
    cl.user_session.set("memory", memory)
    return str(response)

@cl.on_mcp_connect
async def on_mcp_connect(connection):
    """Handler to connec to an MCP server. 
    Lists tools available on the server and connects these tools to
    the LLM agent."""
    
    mcp_tools = cl.user_session.get("mcp_tools", {})
    try:
        mcp_client = BasicMCPClient(connection.url)
        mcp_tool_spec = McpToolSpec(client=mcp_client)
        new_tools = await mcp_tool_spec.to_tool_list_async()
        for tool in new_tools:
            if tool.metadata.name not in mcp_tools:
                mcp_tools[tool.metadata.name] = tool
        agent = cl.user_session.get("agent")
        if isinstance(agent, SimpleChatEngine):
            agent = FunctionCallingAgent.from_tools(
                tools=list(mcp_tools.values()),
                llm=llm,
            )
        
        cl.user_session.set("agent", agent)
        cl.user_session.set("mcp_tools", mcp_tools)
        await cl.Message(f"Connected to MCP server: {connection.name} on {connection.url}").send()

        await cl.Message(
            f"Found {len(new_tools)} tools from {connection.name} MCP server."
        ).send()
    except Exception as e:
        await cl.Message(f"Error listing tools from MCP server: {str(e)}").send()

@cl.on_mcp_disconnect
async def on_mcp_disconnect(name: str):
    """Handler to handle disconnects from an MCP server.
    Updates tool list available for the LLM agent.
    """
    mcp_tools = cl.user_session.get("mcp_tools", {})
    if name in mcp_tools:
        del mcp_tools[name]

    # Update tools list in agent
    if len(mcp_tools)>0:
        agent = FunctionCallingAgent.from_tools(
            tools=list(mcp_tools.values()), #agent still has tools not removed
            llm=llm,
        )
    else:
        agent = SimpleChatEngine.from_defaults(
            llm=llm,
        )
    cl.user_session.set("mcp_tools", mcp_tools)
    cl.user_session.set("agent", agent)
    
    await cl.Message(f"Disconnected from MCP server: {name}").send()