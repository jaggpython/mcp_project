import json
import re

from mcp import Client
from langchain_ollama import ChatOllama


MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


def clean_json_response(content: str) -> str:

    content = content.strip()

    content = re.sub(
        r"^```json\s*",
        "",
        content,
        flags=re.IGNORECASE,
    )

    content = re.sub(
        r"^```\s*",
        "",
        content,
    )

    content = re.sub(
        r"\s*```$",
        "",
        content,
    )

    return content.strip()


async def run_agent(user_message: str):

    steps = []

    # -----------------------------------------------------
    # STEP 1
    # -----------------------------------------------------

    steps.append({
        "icon": "🧠",
        "title": "Agent received the question",
        "description": user_message,
        "status": "completed",
    })


    # -----------------------------------------------------
    # CONNECT TO MCP
    # -----------------------------------------------------

    async with Client(MCP_SERVER_URL) as client:

        # -------------------------------------------------
        # STEP 2 - DISCOVER TOOLS
        # -------------------------------------------------

        tools_response = await client.list_tools()

        tools = tools_response.tools

        tool_names = [
            tool.name
            for tool in tools
        ]

        steps.append({
            "icon": "🔍",
            "title": "Discovered MCP tools",
            "description": ", ".join(tool_names),
            "status": "completed",
        })


        # -------------------------------------------------
        # TOOL INFORMATION
        # -------------------------------------------------

        tool_information = []

        for tool in tools:

            tool_information.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            })


        tools_json = json.dumps(
            tool_information,
            indent=2,
            default=str,
        )


        # -------------------------------------------------
        # PLANNER PROMPT
        # -------------------------------------------------

        planner_prompt = f"""
You are a tool-selection agent.

Your job is ONLY to decide whether the user's request
requires one of the available MCP tools.

Available MCP tools:

{tools_json}

User request:

{user_message}


IMPORTANT RULES:

1. Greetings such as:
   - hello
   - hi
   - hey
   - good morning
   - good evening

   DO NOT require an MCP tool.

2. General conversation does NOT require an MCP tool.

3. Questions about calculations require a calculator tool.

4. Only select a calculator tool when the user clearly
   asks for a mathematical calculation.

5. NEVER select a calculator tool for a greeting.

6. NEVER guess numbers.

7. NEVER invent arguments.

8. If you are unsure whether a tool is required,
   return tool = null.

9. You MUST select the correct tool based on the user's
   actual request.

Calculator tool rules:

add_numbers:
Use for addition.

subtract_numbers:
Use for subtraction.

multiply_numbers:
Use for multiplication.

divide_numbers:
Use for division.


Examples:

User:
hello

Output:
{{"tool": null, "arguments": {{}}}}


User:
hi there

Output:
{{"tool": null, "arguments": {{}}}}


User:
What is 10 + 20?

Output:
{{"tool": "add_numbers", "arguments": {{"a": 10, "b": 20}}}}


User:
Calculate 50 - 10

Output:
{{"tool": "subtract_numbers", "arguments": {{"a": 50, "b": 10}}}}


User:
What is 5 multiplied by 6?

Output:
{{"tool": "multiply_numbers", "arguments": {{"a": 5, "b": 6}}}}


User:
What is 100 divided by 4?

Output:
{{"tool": "divide_numbers", "arguments": {{"a": 100, "b": 4}}}}


Return ONLY valid JSON.

Required format:

{{
    "tool": "tool_name",
    "arguments": {{
        "argument": value
    }}
}}

OR:

{{
    "tool": null,
    "arguments": {{}}
}}

Do not return markdown.
Do not explain your decision.
Do not return any text outside the JSON.
"""


        # -------------------------------------------------
        # ASK OLLAMA
        # -------------------------------------------------

        planning_response = await llm.ainvoke(
            planner_prompt
        )

        planning_text = clean_json_response(
            planning_response.content
        )


        try:

            decision = json.loads(
                planning_text
            )

        except json.JSONDecodeError:

            return {
                "answer": "I could not understand the AI tool selection.",
                "tool": None,
                "steps": steps,
            }


        tool_name = decision.get("tool")

        arguments = decision.get(
            "arguments",
            {},
        )


        # -------------------------------------------------
        # NO TOOL REQUIRED
        # -------------------------------------------------

        if not tool_name:

            steps.append({
                "icon": "💬",
                "title": "No MCP tool required",
                "description": "Ollama decided to answer directly.",
                "status": "completed",
            })


            response = await llm.ainvoke(
                user_message
            )


            steps.append({
                "icon": "🤖",
                "title": "Generated final answer",
                "description": "Ollama generated the response.",
                "status": "completed",
            })


            return {
                "answer": response.content,
                "tool": None,
                "steps": steps,
            }


        # -------------------------------------------------
        # VALIDATE TOOL
        # -------------------------------------------------

        available_tools = {
            tool.name
            for tool in tools
        }


        if tool_name not in available_tools:

            steps.append({
                "icon": "❌",
                "title": "Tool not available",
                "description": tool_name,
                "status": "failed",
            })

            return {
                "answer": f"Tool '{tool_name}' is not available.",
                "tool": tool_name,
                "steps": steps,
            }


        # -------------------------------------------------
        # STEP 3 - TOOL SELECTION
        # -------------------------------------------------

        steps.append({
            "icon": "🎯",
            "title": "Selected MCP tool",
            "description": tool_name,
            "status": "completed",
        })


        # -------------------------------------------------
        # STEP 4 - CALL MCP TOOL
        # -------------------------------------------------

        tool_result = await client.call_tool(
            tool_name,
            arguments,
        )


        result = tool_result.structured_content


        steps.append({
            "icon": "🛠️",
            "title": "Executed MCP tool",
            "description": (
                f"{tool_name}("
                f"{json.dumps(arguments)}"
                ")"
            ),
            "status": "completed",
        })


        # -------------------------------------------------
        # STEP 5 - TOOL RESULT
        # -------------------------------------------------

        steps.append({
            "icon": "📦",
            "title": "Received tool result",
            "description": json.dumps(
                result,
                default=str,
            ),
            "status": "completed",
        })


        # -------------------------------------------------
        # FINAL LLM RESPONSE
        # -------------------------------------------------

        final_prompt = f"""
You are a helpful AI assistant.

User question:
{user_message}

Tool used:
{tool_name}

Tool result:
{json.dumps(result, default=str)}

Answer the user's question using the tool result.

Keep the answer concise and natural.
"""


        final_response = await llm.ainvoke(
            final_prompt
        )


        # -------------------------------------------------
        # STEP 6
        # -------------------------------------------------

        steps.append({
            "icon": "🤖",
            "title": "Generated final answer",
            "description": "Ollama converted the tool result into a natural language response.",
            "status": "completed",
        })


        return {
            "answer": final_response.content,
            "tool": tool_name,
            "arguments": arguments,
            "tool_result": result,
            "steps": steps,
        }