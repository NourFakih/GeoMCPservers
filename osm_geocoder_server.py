import os
import requests
from mcp.server.fastmcp import FastMCP

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"

mcp = FastMCP("OSMGeocoder")

USER_AGENT = os.environ.get("NOMINATIM_USER_AGENT", "map-agents-assignment/1.0")


def _nominatim_get(path: str, params: dict):
    """Call the OpenStreetMap Nominatim API and return JSON."""
    headers = {"User-Agent": USER_AGENT}
    url = f"{NOMINATIM_BASE}{path}"
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def search_place(query: str, limit: int = 5):
    """
    Search for a place name or address using OSM Nominatim.

    Returns a list of matches with display name, coordinates and OSM ids.
    """
    data = _nominatim_get(
        "/search",
        {
            "q": query,
            "format": "json",
            "limit": limit,
            "addressdetails": 1,
        },
    )
    results = []
    for item in data:
        results.append(
            {
                "display_name": item.get("display_name"),
                "lat": float(item["lat"]),
                "lon": float(item["lon"]),
                "osm_type": item.get("osm_type"),
                "osm_id": item.get("osm_id"),
            }
        )
    return results


@mcp.tool()
def reverse_geocode(lat: float, lon: float):
    """
    Reverse-geocode coordinates into a human-readable address.
    """
    data = _nominatim_get(
        "/reverse",
        {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
        },
    )
    return {
        "display_name": data.get("display_name"),
        "address": data.get("address", {}),
        "osm_type": data.get("osm_type"),
        "osm_id": data.get("osm_id"),
    }


@mcp.tool()
def lookup_place(osm_type: str, osm_id: int):
    """
    Look up OSM object details by (osm_type, osm_id).

    osm_type is one of: N (node), W (way), R (relation).
    """
    osm_param = f"{osm_type[0].upper()}{osm_id}"
    data = _nominatim_get(
        "/lookup",
        {
            "osm_ids": osm_param,
            "format": "json",
            "addressdetails": 1,
        },
    )
    if not data:
        return {"error": "No object found"}
    item = data[0]
    return {
        "display_name": item.get("display_name"),
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
        "address": item.get("address", {}),
    }


if __name__ == "__main__":
    # Run with stdio transport for Agents SDK / MCP CLI
    mcp.run()

