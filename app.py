import chainlit as cl
from openai import OpenAI

@cl.on_chat_start
async def on_chat_start():
    client = OpenAI(
        base_url="http://localhost:11434/v1/",
        api_key="ollama", #required but not used.
    )
    cl.user_session.set("client", client)
    cl.user_session.set("history", [])
    cl.user_session.set("mcp_tool_count", 0)

@cl.on_message
async def on_message(message: cl.Message):
    client = cl.user_session.get("client")
    history = cl.user_session.get("history")
    functions = cl.user_session.get("functions", [])
    mcp_tool_count = cl.user_session.get("mcp_tool_count")
    # Append the new message to the history
    history.append({'role':'user', 'content': message.content})
    
    # Check for mcp_tools
    
    mcp_tools = cl.user_session.get("mcp_tools", {})
    if len(mcp_tools) != mcp_tool_count:
        all_tools = [tool for connection_tools in mcp_tools.values() for tool in connection_tools]
        
        for tool in all_tools:
            functions.append(
                {"name": tool.name, "description": tool.description, "parameters": tool.schema}
            )
        cl.user_session.set("functions", functions)
        cl.user_session.set("mcp_tool_count", len(mcp_tools))
        
    response = client.chat.completinos.create(
        model="qwen2.5",
        messages = history,
        tools=functions,
    )