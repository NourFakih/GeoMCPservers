# Map Agents Assignment – Part 2

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

