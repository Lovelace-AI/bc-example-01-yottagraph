"""
Company Analyst Agent — analyzes Apple and Tesla using EDGAR data from
Postgres and live Elemental API data.

Reads stored financial data (synced from EDGAR) and supplements with live
knowledge graph queries for sentiment, relationships, and entity context.

Local testing:
    export ELEMENTAL_API_URL=https://stable-query.lovelace.ai
    export ELEMENTAL_API_TOKEN=<your-token>
    cd agents
    pip install -r company_analyst/requirements.txt
    adk web
"""

import json

from google.adk.agents import Agent

try:
    from broadchurch_auth import elemental_client
except ImportError:
    from .broadchurch_auth import elemental_client


def get_schema() -> dict:
    """Get the knowledge graph schema: entity types (flavors) and properties.

    Call this to discover what kinds of entities exist and what properties
    they have. Returns flavor IDs and property IDs needed for other queries.
    """
    resp = elemental_client.get("/elemental/metadata/schema")
    resp.raise_for_status()
    return resp.json()


def lookup_entity(name: str) -> dict:
    """Look up an entity by name (e.g. 'Apple Inc', 'Tesla Inc', 'Elon Musk').

    Args:
        name: Entity name to search for.

    Returns:
        Entity details including NEIDs and basic properties.
    """
    resp = elemental_client.get(f"/entities/lookup?entityName={name}&maxResults=5")
    resp.raise_for_status()
    return resp.json()


def get_entity_properties(eids: list[str], property_names: list[str]) -> dict:
    """Get property values for one or more entities.

    Args:
        eids: List of entity IDs (NEIDs) to query.
        property_names: List of property names to retrieve.
            Common properties: 'total_revenue', 'net_income', 'total_assets',
            'total_liabilities', 'shareholders_equity', 'shares_outstanding',
            'ticker', 'company_cik', 'filed', 'form_type', 'filing_date'.

    Returns:
        Dict with 'values' array containing property data per entity.
        Each value has: eid, pid, value, recorded_at.
    """
    schema_resp = elemental_client.get("/elemental/metadata/schema")
    schema_resp.raise_for_status()
    schema = schema_resp.json()
    props = schema.get("schema", schema).get("properties", [])
    pid_map = {p["name"]: p["pid"] for p in props}

    pids = [pid_map[n] for n in property_names if n in pid_map]
    if not pids:
        return {"error": f"No matching PIDs for: {property_names}"}

    resp = elemental_client.post(
        "/elemental/entities/properties",
        data={
            "eids": json.dumps(eids),
            "pids": json.dumps(pids),
            "include_attributes": "true",
        },
    )
    resp.raise_for_status()
    return resp.json()


def find_entities(expression: str, limit: int = 10) -> dict:
    """Search for entities using the expression language.

    Args:
        expression: JSON string with search criteria. Examples:
            - By type: {"type": "is_type", "is_type": {"fid": 10}}
            - Natural language: {"type": "natural_language", "natural_language": "tech companies"}
            - Combine: {"type": "and", "and": [<expr1>, <expr2>]}
        limit: Max results (default 10).

    Returns:
        Dict with 'eids' (entity IDs) and 'op_id'.
    """
    resp = elemental_client.post(
        "/elemental/find",
        data={"expression": expression, "limit": str(limit)},
    )
    resp.raise_for_status()
    return resp.json()


def get_linked_entities(neid: str, entity_type: str = "organization") -> dict:
    """Get entities linked to a given entity.

    Args:
        neid: The source entity's NEID.
        entity_type: Type of linked entities to return.
            Only 'person', 'organization', 'location' are supported.

    Returns:
        List of linked entities with names and relationship types.
    """
    resp = elemental_client.get(
        f"/entities/{neid}/linked",
        params={"entity_type": entity_type},
    )
    resp.raise_for_status()
    return resp.json()


root_agent = Agent(
    model="gemini-2.0-flash",
    name="company_analyst",
    instruction="""You are a financial analyst specializing in Apple (AAPL) and Tesla (TSLA).

You have access to:
1. The Lovelace Knowledge Graph via the Elemental API - use this for entity data,
   financial properties, relationships, and schema discovery.
2. Tools to look up entities, get their properties, find related entities,
   and explore the knowledge graph schema.

Your capabilities:
- Look up Apple and Tesla in the knowledge graph
- Retrieve financial metrics: total_revenue, net_income, total_assets,
  total_liabilities, shareholders_equity, shares_outstanding
- Compare companies across financial dimensions
- Find related entities (officers, subsidiaries, linked organizations)
- Analyze trends from historical property values (each value has a recorded_at date)

When answering questions:
- Use actual data from the knowledge graph, not assumptions
- Present financial figures clearly (e.g., "$307B" not "307000000000")
- When comparing companies, use side-by-side format
- Note the filing dates so the user knows how recent the data is
- If asked about something outside Apple/Tesla, use the search tools to find it

Start by understanding what the user wants to know, then use the appropriate
tools. If you need to discover what properties are available, use get_schema first.""",
    tools=[
        get_schema,
        lookup_entity,
        get_entity_properties,
        find_entities,
        get_linked_entities,
    ],
)
