#%%

from fastmcp import FastMCP, Context
from fastmcp.resources import DirectoryResource

from openai import OpenAI
from llama_index.core import SimpleDirectoryReader

from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Initialize FastMCP and register the docs directory
mcp = FastMCP(name="Writing tools")
docs_dir = Path(__file__).parents[1] / "docs"
directory_resource = DirectoryResource(
    uri="resource://docs",
    path=docs_dir.resolve(),
    name="Docs folder",
    description="Essays and other documents",
    recursive=True
)
mcp.add_resource(directory_resource)

# 2. Initialize your LLM client
llm_client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)

#%%
@mcp.tool()
async def generate_poem(topic: str, language: str) -> str:
    """Generates a short poem about a given topic"""
    payload = [
        {"role": "system", "content": "You are a talented poet who writes concise, evocative prose."},
        {"role": "user",   "content": f"Write a short poem about {topic} in {language}"}
    ]
    response = llm_client.chat.completions.create(
        messages=payload,
        model="qwen2.5"
    )
    return response.choices[0].message.content

@mcp.tool()
async def chat_with_docs(
    question: str,
    doc_name: str,
    context: Context,
) -> str:
    """
    Allows users to ask questions about documents in the 'docs' resource.
    'doc_name' can be a full or partial filename (e.g. 'paul_graham').
    """
    logger.info("Reading directory resource...")
    listing_res = await context.read_resource(directory_resource.uri)
    logger.info("Directory resource read successfully.")
    
    # content is a JSON array of { name, uri, mimeType, size, ... }
    raw = listing_res[0].content
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    entries = json.loads(raw)
    logger.info(entries)
    
    match = None
    for entry in entries:
        if isinstance(entries[entry], list):
            for item in entries[entry]:
                if doc_name.lower() in item.lower():
                    match = item
                    break
            break
        else:
            if doc_name.lower() in entries[entry].lower():
                match = entries[entry]
                break
    
    if not match:
        return f"❌ No document matching '{doc_name}' found under resource://docs"
    logger.info(f"Found match {match}")
    
    file_uri = docs_dir / match
    logger.info(f"Reading file at: {file_uri}")
    
    docs = SimpleDirectoryReader(
        input_files=[f"{docs_dir}/paul_graham_essay.txt"],
    ).load_data()

    # 3. Construct prompt to answer the question
    prompt = (
        "You are a helpful assistant. Use the provided document to answer the question.\n"
        f"Document content:\n{docs[0].text}\n\n"
        f"Question: {question}"
    )
    response = llm_client.chat.completions.create(
        messages=[
            {"role": "system",  "content": prompt}
        ],
        model="qwen2.5"
    )
    return response.choices[0].message.content

# 5. Start the server
if __name__ == "__main__":
    mcp.run(transport="sse")
