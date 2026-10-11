"""MCP server exposing the catalogue to a coding agent.

Read-only on purpose. An agent working on this repo often needs to know what is in the
catalogue to write a sensible test or check a filter; it has no business adding units.

Run it over stdio:

    python mcp-server/server.py

Point it at a running backend with CATALOG_API_URL, default http://localhost:8000.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = os.getenv("CATALOG_API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 10

TOOLS = [
    {
        "name": "search_equipment",
        "description": "Filter the catalogue by category, refrigerant, manufacturer "
                       "and a capacity window in kW.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "enum": ["chiller", "compressor",
                                                        "heat_exchanger",
                                                        "circulator_pump", "fan_coil"]},
                "refrigerant": {"type": "string"},
                "manufacturer": {"type": "string"},
                "min_capacity": {"type": "number", "minimum": 0},
                "max_capacity": {"type": "number", "minimum": 0},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 20},
            },
        },
    },
    {
        "name": "get_equipment",
        "description": "Full specification for one model code, including computed COP.",
        "inputSchema": {
            "type": "object",
            "properties": {"model": {"type": "string"}},
            "required": ["model"],
        },
    },
    {
        "name": "compare_equipment",
        "description": "Compare 2 to 4 model codes and get the better figure marked per field.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "models": {"type": "array", "items": {"type": "string"},
                           "minItems": 2, "maxItems": 4},
            },
            "required": ["models"],
        },
    },
    {
        "name": "list_facets",
        "description": "Distinct categories, refrigerants, manufacturers and the capacity range.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def fetch(path, params=None):
    url = f"{API}{path}"
    if params:
        clean = {k: v for k, v in params.items() if v is not None}
        if clean:
            url += "?" + urllib.parse.urlencode(clean)
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode("utf-8", "replace")[:400]}
    except urllib.error.URLError as e:
        return {"error": "backend unreachable", "detail": str(e.reason)}


def call_tool(name, args):
    if name == "search_equipment":
        return fetch("/equipment", {
            "category": args.get("category"),
            "refrigerant": args.get("refrigerant"),
            "manufacturer": args.get("manufacturer"),
            "min_capacity": args.get("min_capacity"),
            "max_capacity": args.get("max_capacity"),
            "limit": args.get("limit", 20),
        })
    if name == "get_equipment":
        return fetch(f"/equipment/{urllib.parse.quote(args['model'], safe='')}")
    if name == "compare_equipment":
        return fetch("/equipment/compare", {"models": ",".join(args["models"])})
    if name == "list_facets":
        return fetch("/facets")
    return {"error": f"unknown tool {name}"}


def respond(message_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": message_id, "result": result}) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        message = json.loads(line)
        method = message.get("method")
        message_id = message.get("id")

        if method == "initialize":
            respond(message_id, {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "hvacr-catalog", "version": "1.0.0"},
            })
        elif method == "tools/list":
            respond(message_id, {"tools": TOOLS})
        elif method == "tools/call":
            params = message.get("params", {})
            payload = call_tool(params.get("name"), params.get("arguments", {}))
            respond(message_id, {
                "content": [{"type": "text", "text": json.dumps(payload, indent=2)}],
                "isError": "error" in payload,
            })
        elif message_id is not None:
            respond(message_id, {})


if __name__ == "__main__":
    main()
