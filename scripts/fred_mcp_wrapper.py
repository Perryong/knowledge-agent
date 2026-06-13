"""Minimal FRED MCP server using requests (synchronous) — bypasses anyio/TLS issues on Windows."""
import os, json, requests
from mcp.server.fastmcp import FastMCP

API_KEY = os.environ.get("FRED_API_KEY", "")
BASE = "https://api.stlouisfed.org/fred"

mcp = FastMCP("fred")


def _get(path, **params):
    params["api_key"] = API_KEY
    params["file_type"] = "json"
    r = requests.get(f"{BASE}/{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def fred_series(
    operation: str,
    series_id: str = "",
    search_text: str = "",
    limit: int = 100,
    offset: int = 0,
    tag_name: str = "",
    release_id: int = 0,
    source_id: int = 0,
    category_id: int = 0,
) -> dict:
    """Fetch FRED series data and metadata.

    Operations: get, search, get_observations, get_categories, get_release,
    get_tags, search_tags, get_updates, get_vintage_dates
    """
    if operation == "get":
        return _get("series", series_id=series_id)
    if operation == "get_observations":
        return _get("series/observations", series_id=series_id, limit=limit, offset=offset)
    if operation == "search":
        return _get("series/search", search_text=search_text, limit=limit, offset=offset)
    if operation == "get_categories":
        return _get("series/categories", series_id=series_id)
    if operation == "get_release":
        return _get("series/release", series_id=series_id)
    if operation == "get_tags":
        return _get("series/tags", series_id=series_id)
    if operation == "search_tags":
        return _get("tags/series", tag_names=tag_name, limit=limit)
    if operation == "get_updates":
        return _get("series/updates", limit=limit, offset=offset)
    if operation == "get_vintage_dates":
        return _get("series/vintagedates", series_id=series_id)
    if operation == "get_categories":
        return _get("category", category_id=category_id)
    if operation == "get_release":
        return _get("release", release_id=release_id)
    if operation == "get_source":
        return _get("source", source_id=source_id)
    supported = ["get","search","get_observations","get_categories","get_release",
                 "get_tags","search_tags","get_updates","get_vintage_dates"]
    return {"error": {"code": "INVALID_OPERATION", "message": f"Unsupported operation '{operation}'",
                      "details": {"supported_operations": supported}}}


if __name__ == "__main__":
    mcp.run(transport="stdio")
