# Part 1
The Hugging Face article presents the Model Context Protocol (MCP) as an open, model-agnostic standard for connecting AI agents to external tools, data sources, and workflows. MCP addresses the long-standing “integration problem”: previously, developers had to build one-off API integrations, plugins, or framework-specific tools for each service the model needed to access.

 Instead, MCP defines a client–server architecture where an AI application (the host) runs an MCP client that discovers and talks to MCP servers, which expose tools, resources, and prompt templates through a standardized schema. This enables dynamic discovery: when a new MCP server is started (for example, for a CRM or database), the agent can immediately detect its capabilities without code changes.


The article emphasizes that MCP is not an agent framework or planner; it sits in the “Action” layer of agentic workflows, acting as plumbing that lets agents perform operations like querying databases, fetching files, or calling APIs.

 It reduces integration complexity from an N×M problem (N models × M tools) to N+M by standardizing how tools are exposed.

 At the same time, the author notes trade-offs: running multiple local or remote servers introduces operational overhead; models can still misuse tools if descriptions are poor; the protocol is evolving; and security and governance (authentication, logging, and permissions) are still active areas of work.

Existing map servers illustrate useful patterns for designing MCP servers. OpenStreetMap and its ecosystem center on a tiled architecture: web maps fetch raster or vector tiles from HTTP endpoints following a standard {z}/{x}/{y} URL pattern, separating rendering on the client from data serving on the backend.

 Providers built on OSM, such as Geoapify, expose many different visual styles (e.g., “osm-carto,” “positron,” “dark-matter”) via style JSON documents and tile endpoints that are parameterized by zoom, x/y coordinates, and API keys.
 Libraries like MapLibre GL JS consume vector tiles and styles to render interactive, GPU-accelerated maps in the browser, while plugins add geocoding, search, and navigation controls.

 More advanced setups use dedicated tile servers (e.g., Martin) behind MapLibre frontends and support layering of GeoJSON, raster, and vector data.

Across these systems, common design patterns emerge: stateless HTTP APIs, clear URL and parameter conventions, separation of concerns between data serving and rendering, and composable “operations” such as tile retrieval, geocoding, and routing. These map naturally to MCP “tools” and operations for your assignment’s custom map servers.

# Part 2

This folder contains a small OpenAI Agents SDK project implementing two MCP map servers and a simple CLI interface for demo/screencast.

## Components

- `osm_geocoder_server.py` – MCP server wrapping OpenStreetMap Nominatim:
  - `search_place(query, limit)` – forward geocoding.
  - `reverse_geocode(lat, lon)` – reverse geocoding.
  - `lookup_place(osm_type, osm_id)` – lookup by OSM id.
- `routing_server.py` – MCP server wrapping OpenRouteService directions:
  - `route_coords(...)` – full GeoJSON route.
  - `route_distance(...)` – distance and duration only.
  - `route_summary(...)` – simplified step list for directions.
- `map_agent.py` – Assistant agent that connects to both servers and exposes a text (CLI) interface.
- `map_agent_gradio.py` – Same agent exposed via a Gradio web chat UI.

## Setup

From the project root (the folder containing this `map_agents` directory):

```bash
cd map_agents
py -3.13 -m venv .venv
.\.venv\Scripts\activate
pip install openai-agents "mcp[cli]" requests
```

For the Gradio UI, also install:

```powershell
pip install gradio python-dotenv
```

Set required environment variables (PowerShell examples):

```powershell
$env:OPENAI_API_KEY = "sk-..."       # your OpenAI API key
$env:ORS_API_KEY = "your_ors_key"    # OpenRouteService key
$env:NOMINATIM_USER_AGENT = "c5-assignment-yourname/1.0"
```

## Run the demo agent

### CLI version

```powershell
cd map_agents
py -3.13 .\map_agent.py
```

Then type natural language queries, for example:

- `Find the coordinates of the Statue of Liberty.`
- `Reverse geocode 40.6892, -74.0445.`
- `Give me the driving distance and ETA from Berlin to Hamburg.`

Type `quit` to exit. This CLI is suitable for recording the Part 3 screencast: show the terminal, run a few queries, and explain how the agent uses the two MCP servers.

### Gradio web UI

```powershell
cd map_agents
py -3.13 .\map_agent_gradio.py
```

Then open the local URL Gradio prints (by default http://127.0.0.1:7860/) in your browser and chat with the same MapAssistant agent using a graphical interface. This is convenient for your video recording: you can show the map-related questions and answers in the browser instead of the terminal.

# Part 3