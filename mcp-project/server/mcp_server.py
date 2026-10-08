from mcp.server.mcpserver import MCPServer

from tools.calculator import (
    add,
    subtract,
    multiply,
    divide,
)


mcp = MCPServer(
    "Calculator Server",
    version="1.0.0",
)


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return add(a, b)


@mcp.tool()
def subtract_numbers(a: int, b: int) -> int:
    """Subtract two numbers."""
    return subtract(a, b)


@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers."""
    return multiply(a, b)


@mcp.tool()
def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers."""

    if b == 0:
        raise ValueError("Cannot divide by zero")

    return divide(a, b)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
    )