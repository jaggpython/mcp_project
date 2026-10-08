import asyncio

from mcp import Client


MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"


async def main():

    print("Connecting to MCP server...")

    async with Client(MCP_SERVER_URL) as client:

        print("Connected to MCP server.")

        # Get available tools
        tools_response = await client.list_tools()

        print("\nAvailable MCP Tools:")

        for tool in tools_response.tools:

            print(f"\n- {tool.name}")
            print(f"  {tool.description}")

        # Test calculator tool
        print("\nCalling add_numbers...")

        result = await client.call_tool(
            "add_numbers",
            {
                "a": 10,
                "b": 20,
            },
        )

        print("\nTool Result:")

        print(result)


if __name__ == "__main__":

    asyncio.run(main())