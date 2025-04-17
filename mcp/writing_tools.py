#%%
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

# resume_path = Path(
#     "~/Documents/Lim Hsien Yong (Titus) Resume.pdf"
# ).expanduser().resolve()

# resume_resource = FileResource(
#     uri=f"file://{resume_path.as_posix()}",
#     path = resume_path,
#     name="Resume",
#     description="Titus Lim's resume",
#     mime_type="bytes/pdf",
#     tags={"resume", "pdf"},
# )

# mcp.add_resource(resume_resource)

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

@mcp.tool()
async def generate_professional_summary(
    resume_uri: str,
    context: Context,
) -> str:
    """Generates a cover letter based on a resume"""
    doc_resource = await context.read_resource(resume_uri)
    doc_content = doc_resource[0].content
    response = await context.sample(
        f"Write a cover letter based on the following resume: {doc_content}",
        system_prompt = "You are a professional resume writer who writes compelling professional summaries from resumes."
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