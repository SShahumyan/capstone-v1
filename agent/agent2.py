"""Agent loop, tool definitions and dispatcher."""

import json
from google import genai
from openai import OpenAI
from search_agent import search

from dotenv import load_dotenv
import os

load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── Tool definitions ──────────────────────────────────────────────────────────

tools = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Does a vector search from db that contains court case document",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "query for semantic search"},
                    "k": {"type": int, "description": "number of returned nearest vectors. The default value is 5"}
                },
                "required": ["query"]
            }
        }
    }
]

# ── Tool dispatcher ───────────────────────────────────────────────────────────

def dispatch_tool(name: str, args: dict) -> str:
    """Route tool call from LLM to the correct Python function."""
    dispatch = {
        "search":           lambda: search(**args),
    }
    fn = dispatch.get(name)
    if not fn:
        return "Unknown tool."
    return fn()

# ── Agent loop ────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
        Role & Task
You are an AI legal assistant specialized in analyzing court cases. Your primary task is to perform vector retrieval from a database containing legal documentation to answer user inquiries accurately.

Language Protocol

    User Interaction: You must communicate with the user exclusively in Armenian.

    Search Queries: When using the retrieval tool, you must formulate your queries in Armenian to ensure they match the language of the indexed documents.

    Tone: Maintain a professional, formal, and objective tone suitable for legal assistance.

Operational Instructions

    Analyze: Carefully evaluate the user's request in Armenian.

    Retrieve: Gather information from the vector search tool. You have the autonomy to decide how many search iterations are required to provide a comprehensive answer.

    Query Generation: Determine the most effective Armenian keywords or questions to ask the database to find relevant sections of the court case.

    Synthesize: Combine the retrieved data into a clear, concise Armenian response. If the information is not present in the database, state that clearly in Armenian.
    """


def ask_agent(user_message: str, messages: list = None) -> tuple[str, list]:
    """Send user message to agent. Agent calls tools as needed and returns final response."""
    if messages is None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    messages.append({"role": "user", "content": user_message})

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if not message.tool_calls:
            messages.append({"role": "assistant", "content": message.content})
            return message.content, messages

        message_dict = message.model_dump()
        messages.append(message_dict)
        for tool_call in message_dict["tool_calls"]:
            name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])
            result = dispatch_tool(name, args)
            print(f"tool used: {name}({args}) \n{result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })
    