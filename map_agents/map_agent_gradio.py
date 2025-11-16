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
    Gradio chat handler.

    Each user message is handled independently; the agent does not keep
    conversation state between turns (stateless, as in the assignment).
    ChatInterface manages the history; we just return the assistant reply.
    """
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

        # Single-turn call: just pass the current user message
        result = await Runner.run(agent, message)

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
