#%%
import os
from fastmcp import FastMCP, Context
from fastmcp.resources import FileResource
from fastmcp.client.sampling import (
    RequestContext,
    SamplingMessage,
    SamplingParams
)
from openai import OpenAI

from typing import List
from pathlib import Path

mcp = FastMCP(
    name = "Writing tools",
)

__curdir__ = os.getcwd()
if "mcp" in __curdir__:
    file_path = Path(
        "../docs/paul_graham_essay.txt"
    ).resolve()
else:
    file_path = Path(
        "./docs/paul_graham_essay.txt"
    ).resolve()

file_resource = FileResource(
    uri=f"file://{file_path.as_posix()}",
    path = file_path,
    name="Paul Graham's essay",
    description="Paul Graham's personal essay",
    mime_type="text/markdown",
    tags={"essay"}
)

mcp.add_resource(file_resource)
print("resource added!")

## Invoking Ollama from OpenAI!
llm_client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama", #required but not used.
)

@mcp.tool()
async def generate_poem(topic: str, context: Context) -> str:
    """Generates a short poem about a given topic"""
    response = await context.sample(
        f"Write a short poem about {topic}",
        system_prompt = "You are a talented poet who writes concise, evocative prose."
    )
    return response

@mcp.tool() #fix the name of the tool
async def generate_summary(
    context: Context,
    doc_uri: str = file_resource.uri,
) -> str:
    """Generates a summary based on a document"""
    doc_resource = await context.read_resource(doc_uri)
    doc_content = doc_resource[0].content
    response = await context.sample(
        f"Summarize the following document: {doc_content}",
        system_prompt = "You are a professional writer who excels at distilling essentials from essays."
    )
    return response

## -- CLIENT SIDE --
async def sampling_handler(
    messages: List[SamplingMessage],
    params: SamplingParams,
    ctx: RequestContext,
) -> str:
    """Handle sampling requests from the server using the LLM client."""
    
    system_instruction = params.systemPrompt or "You are a helpful assistant"
    payload = [{"role": "system", "content": system_instruction}]
    for m in messages:
        if m.content.type == "text":
            payload.append({"role": "user", "content": m.content.text})
    print(messages)
    response = llm_client.chat.completions.create(
        messages = payload,
        model="qwen2.5"
    )
    return response.choices[0].message.content

#%%
if __name__ == "__main__":
    print("🚀Starting server... ")
    mcp.run(transport="sse")