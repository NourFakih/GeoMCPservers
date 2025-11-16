import os
import sys
from typing import List, Tuple

import gradio as gr
from dotenv import load_dotenv

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from agents.model_settings import ModelSettings


# Load environment variables from .env (OPENAI_API_KEY, ORS_API_KEY, etc.)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

PYTHON_CMD = sys.executable or "python"


async def chat(
    message: str, history: List[Tuple[str, str]]
) -> str:
    """
    Gradio chat handler with short-term memory.

    We build a short text context from the last few turns and include it
    in the user message sent to the agent, so follow-up questions can
    reference the same place or route.
    """
    # Build short in-message context from recent history
    max_turns = 4
    recent = history[-max_turns:] if history else []
    lines: list[str] = []
    for user_msg, assistant_msg in recent:
        lines.append(f"User: {user_msg}")
        if assistant_msg:
            lines.append(f"Assistant: {assistant_msg}")
    lines.append(f"User: {message}")
    message_with_context = "\n".join(lines)

    async with MCPServerStdio(
        name="OSMGeocoder",
        params={
            "command": PYTHON_CMD,
            "args": ["osm_geocoder_server.py"],
        },
        cache_tools_list=True,
    ) as osm_server, MCPServerStdio(
        name="RoutingServer",
        params={
            "command": PYTHON_CMD,
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

        # Send the message with embedded short history context
        result = await Runner.run(agent, message_with_context)

    return result.final_output


demo = gr.ChatInterface(
    fn=chat,
    title="MapAssistant (MCP + Gradio)",
    description=(
        "Ask for geocoding, reverse geocoding, and routing.\n"
        "Backed by MCP servers for OpenStreetMap Nominatim and OpenRouteService."
    ),
    examples=[
        "What are the coordinates of the Eiffel Tower?",
        "Reverse geocode 40.6892, -74.0445.",
        "Driving distance and ETA from Berlin to Hamburg.",
    ],
)


if __name__ == "__main__":
    # share=False keeps it local; set share=True if you want a public link.
    demo.launch()
