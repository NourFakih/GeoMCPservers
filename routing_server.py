import os
import requests
from mcp.server.fastmcp import FastMCP

ORS_BASE = "https://api.openrouteservice.org"
ORS_KEY = os.environ.get("ORS_API_KEY")  # set this in your env

mcp = FastMCP("RoutingServer")


class RoutingError(Exception):
    pass


def _ors_directions(start, end, profile: str = "driving-car"):
    """
    Call the OpenRouteService directions API and return GeoJSON.

    start / end are (lat, lon) tuples.
    """
    if not ORS_KEY:
        raise RoutingError("Missing ORS_API_KEY environment variable")

    url = f"{ORS_BASE}/v2/directions/{profile}/geojson"
    headers = {"Authorization": ORS_KEY}
    body = {
        "coordinates": [
            [start[1], start[0]],  # ORS expects [lon, lat]
            [end[1], end[0]],
        ]
    }
    resp = requests.post(url, json=body, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def route_coords(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    profile: str = "driving-car",
):
    """
    Get a full route between two coordinates as GeoJSON.

    profile examples: driving-car, cycling-regular, foot-walking, ...
    """
    data = _ors_directions(
        (start_lat, start_lon),
        (end_lat, end_lon),
        profile=profile,
    )
    # Return the whole GeoJSON feature collection
    return data


@mcp.tool()
def route_distance(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    profile: str = "driving-car",
):
    """
    Return only distance (meters) and duration (seconds) for a route.
    """
    data = _ors_directions(
        (start_lat, start_lon),
        (end_lat, end_lon),
        profile=profile,
    )
    # ORS returns distance/duration in the first feature, first segment
    props = data["features"][0]["properties"]["segments"][0]
    return {
        "distance_m": props["distance"],
        "duration_s": props["duration"],
    }


@mcp.tool()
def route_summary(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    profile: str = "driving-car",
):
    """
    Return a high-level textual description of the route.

    The LLM can turn this structured list into natural-language directions.
    """
    data = _ors_directions(
        (start_lat, start_lon),
        (end_lat, end_lon),
        profile=profile,
    )
    steps = data["features"][0]["properties"]["segments"][0]["steps"]
    simple_steps = []
    for s in steps:
        simple_steps.append(
            {
                "distance_m": s["distance"],
                "duration_s": s["duration"],
                "instruction": s.get("instruction"),
            }
        )
    return simple_steps


if __name__ == "__main__":
    mcp.run()

