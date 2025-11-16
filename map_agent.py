import asyncio
import os
import sys

from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from agents.model_settings import ModelSettings


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def main() -> None:
    """CLI interface for the MapAssistant agent with short-term memory.

    Uses a single conversation_id so the assistant can remember recent
    context across multiple turns in the same session.
    """
    python_cmd = sys.executable or "python"
    conversation_id = "mapassistant-cli-session"

    # Launch both MCP servers via stdio
    async with MCPServerStdio(
        name="OSMGeocoder",
        params={
            "command": python_cmd,
            "args": ["osm_geocoder_server.py"],
        },
        cache_tools_list=True,
    ) as osm_server, MCPServerStdio(
        name="RoutingServer",
        params={
            "command": python_cmd,
            "args": ["routing_server.py"],
        },
        cache_tools_list=True,
    ) as routing_server:

        agent = Agent(
            name="MapAssistant",
            instructions=(
                "You are a mapping assistant. "
                "Use the MCP tools to geocode places and compute routes. "
                "Prefer tools from OSMGeocoder for search/reverse geocode, "
                "and RoutingServer for distances and directions."
            ),
            mcp_servers=[osm_server, routing_server],
            model_settings=ModelSettings(tool_choice="auto"),
        )

        print(
            "MapAssistant is ready.\n"
            "- Ask for coordinates, addresses, or routes.\n"
            "- Examples:\n"
            '  • "What are the coordinates of the Eiffel Tower?"\n'
            '  • "Route from Berlin to Hamburg by car and give me distance."\n'
            "- Type 'quit' to exit.\n"
        )

        # Interactive loop for demonstration / screencast
        while True:
            try:
                user = input("User> ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting MapAssistant.")
                break

            if not user.strip():
                continue
            if user.lower() in {"q", "quit", "exit"}:
                print("Goodbye.")
                break

            result = await Runner.run(
                agent,
                user,
                conversation_id=conversation_id,
            )
            print("\nAssistant:\n", result.final_output)
            print()


if __name__ == "__main__":
    asyncio.run(main())
