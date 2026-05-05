# agent.py
from google import genai
from google.genai import types
import json
from search_agent import search
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3-flash-preview"

SYSTEM_PROMPT = """You are a helpful assistant with access to a semantic search tool over an Armenian legal document corpus.

When a user asks a question, use the search tool to find relevant passages from the legal documents, then answer based on what you find.

Guidelines:
- Always search before answering questions about the document content
- Cite the page number when referencing retrieved passages
- If search results are not relevant to the question, say so honestly
- You may search multiple times with different queries if needed
- Respond in Armenian language."""

search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search",
            description="Search the Armenian legal document corpus using semantic similarity. Returns the most relevant text chunks for a given query.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description="The search query in Armenian"
                    ),
                    "k": types.Schema(
                        type=types.Type.INTEGER,
                        description="Number of results to return (default 5)"
                    )
                },
                required=["query"]
            )
        )
    ]
)

def run_tool(name: str, args: dict) -> str:
    if name == "search":
        result = search(**args)
        return json.dumps(result, ensure_ascii=False, indent=2)
    return json.dumps({"error": f"Unknown tool: {name}"})

def chat():
    conversation_history = []

    print("\n=== Armenian Legal Document Search Agent (Gemini) ===")
    print("Type your question in Armenian or English.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye.")
            break

        conversation_history.append(
            types.Content(role="user", parts=[types.Part(text=user_input)])
        )

        # Agentic loop
        while True:
            response = client.models.generate_content(
                model=MODEL,
                contents=conversation_history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[search_tool],
                )
            )

            candidate = response.candidates[0].content
            conversation_history.append(candidate)

            # Check for tool calls
            tool_calls = [p for p in candidate.parts if p.function_call is not None]
            text_parts = [p for p in candidate.parts if p.text]

            if tool_calls:
                # Execute all tool calls and collect results
                tool_result_parts = []
                for part in tool_calls:
                    fc = part.function_call
                    print(f"  [searching: \"{fc.args.get('query', '')}\"...]")
                    result = run_tool(fc.name, dict(fc.args))
                    tool_result_parts.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=fc.name,
                                response={"result": result}
                            )
                        )
                    )

                conversation_history.append(
                    types.Content(role="user", parts=tool_result_parts)
                )
                continue

            # No tool calls — final answer
            if text_parts:
                final_text = "".join(p.text for p in text_parts)
                print(f"\nAgent: {final_text}\n")

            break

if __name__ == "__main__":
    chat()