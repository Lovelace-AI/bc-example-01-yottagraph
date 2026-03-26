"""
Company Analyst Agent — analyzes Apple and Tesla using live Elemental API data.

Provides financial comparisons, filing lookups, and relationship exploration
for the two tracked companies. Tools use pre-resolved entity IDs to avoid
lookup failures.

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

COMPANIES = {
    "apple": {"neid": "00508379502570440213", "ticker": "AAPL", "name": "Apple Inc"},
    "tesla": {"neid": "04770104648640614357", "ticker": "TSLA", "name": "Tesla Inc"},
}

FINANCIAL_PROPERTIES = [
    "total_revenue",
    "net_income",
    "total_assets",
    "total_liabilities",
    "shareholders_equity",
    "shares_outstanding",
]

_pid_cache: dict[str, int] | None = None


def _get_pid_map() -> dict[str, int]:
    global _pid_cache
    if _pid_cache is not None:
        return _pid_cache
    resp = elemental_client.get("/elemental/metadata/schema")
    resp.raise_for_status()
    schema = resp.json()
    props = schema.get("schema", schema).get("properties", [])
    _pid_cache = {p["name"]: p["pid"] for p in props}
    return _pid_cache


def _resolve_company(company: str) -> dict | None:
    key = company.lower().strip()
    for k, v in COMPANIES.items():
        if k in key or v["ticker"].lower() in key:
            return v
    return None


def _format_usd(value) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1e12:
        return f"{sign}${v / 1e12:.1f}T"
    if v >= 1e9:
        return f"{sign}${v / 1e9:.1f}B"
    if v >= 1e6:
        return f"{sign}${v / 1e6:.1f}M"
    return f"{sign}${v:,.0f}"


def get_financials(company: str) -> str:
    """Get the latest financial metrics for a company.

    Args:
        company: Company name or ticker — "Apple", "Tesla", "AAPL", or "TSLA".

    Returns:
        Formatted financial summary with the most recent values and their dates.
    """
    co = _resolve_company(company)
    if not co:
        return f"Unknown company '{company}'. I track Apple (AAPL) and Tesla (TSLA)."

    try:
        pid_map = _get_pid_map()
        pids = [pid_map[n] for n in FINANCIAL_PROPERTIES if n in pid_map]
        reverse = {pid_map[n]: n for n in FINANCIAL_PROPERTIES if n in pid_map}

        resp = elemental_client.post(
            "/elemental/entities/properties",
            data={
                "eids": json.dumps([co["neid"]]),
                "pids": json.dumps(pids),
                "include_attributes": "true",
            },
        )
        resp.raise_for_status()
        data = resp.json()

        latest: dict[str, tuple] = {}
        for v in data.get("values", []):
            prop = reverse.get(v["pid"])
            if not prop:
                continue
            date = v.get("recorded_at", "")[:10]
            if prop not in latest or date > latest[prop][1]:
                latest[prop] = (v["value"], date)

        lines = [f"=== {co['name']} ({co['ticker']}) — Latest Financials ===\n"]
        for prop in FINANCIAL_PROPERTIES:
            if prop in latest:
                val, date = latest[prop]
                label = prop.replace("_", " ").title()
                lines.append(f"  {label}: {_format_usd(val)}  (as of {date})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching financials for {co['name']}: {e}"


def compare_companies(property_name: str = "total_revenue") -> str:
    """Compare Apple and Tesla on a specific financial metric.

    Args:
        property_name: The metric to compare. Options:
            total_revenue, net_income, total_assets, total_liabilities,
            shareholders_equity, shares_outstanding.

    Returns:
        Side-by-side comparison with the most recent values.
    """
    try:
        pid_map = _get_pid_map()
        pid = pid_map.get(property_name)
        if not pid:
            return f"Unknown property '{property_name}'. Valid: {', '.join(FINANCIAL_PROPERTIES)}"

        neids = [co["neid"] for co in COMPANIES.values()]
        resp = elemental_client.post(
            "/elemental/entities/properties",
            data={
                "eids": json.dumps(neids),
                "pids": json.dumps([pid]),
                "include_attributes": "true",
            },
        )
        resp.raise_for_status()
        data = resp.json()

        neid_to_name = {co["neid"]: co["name"] for co in COMPANIES.values()}
        latest: dict[str, tuple] = {}
        for v in data.get("values", []):
            eid = v["eid"]
            date = v.get("recorded_at", "")[:10]
            name = neid_to_name.get(eid, eid)
            if name not in latest or date > latest[name][1]:
                latest[name] = (v["value"], date)

        label = property_name.replace("_", " ").title()
        lines = [f"=== {label} Comparison ===\n"]
        for name, (val, date) in sorted(latest.items()):
            lines.append(f"  {name}: {_format_usd(val)}  (as of {date})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error comparing companies: {e}"


def get_filings(company: str) -> str:
    """Get recent SEC filings for a company.

    Args:
        company: Company name or ticker — "Apple", "Tesla", "AAPL", or "TSLA".

    Returns:
        List of recent filings with form type, date, and accession number.
    """
    co = _resolve_company(company)
    if not co:
        return f"Unknown company '{company}'. I track Apple (AAPL) and Tesla (TSLA)."

    try:
        pid_map = _get_pid_map()
        filed_pid = pid_map.get("filed")
        if not filed_pid:
            return "Cannot find 'filed' relationship in schema."

        resp = elemental_client.post(
            "/elemental/entities/properties",
            data={
                "eids": json.dumps([co["neid"]]),
                "pids": json.dumps([filed_pid]),
            },
        )
        resp.raise_for_status()
        data = resp.json()

        doc_neids = []
        for v in data.get("values", []):
            neid = str(v["value"]).zfill(20)
            doc_neids.append((neid, v.get("recorded_at", "")[:10]))

        doc_neids.sort(key=lambda x: x[1], reverse=True)
        doc_neids = doc_neids[:20]

        if not doc_neids:
            return f"No filings found for {co['name']}."

        form_pid = pid_map.get("form_type")
        date_pid = pid_map.get("filing_date")
        acc_pid = pid_map.get("accession_number")
        name_pid = pid_map.get("name")
        batch_pids = [p for p in [form_pid, date_pid, acc_pid, name_pid] if p]
        batch_eids = [n for n, _ in doc_neids]

        props_resp = elemental_client.post(
            "/elemental/entities/properties",
            data={
                "eids": json.dumps(batch_eids),
                "pids": json.dumps(batch_pids),
            },
        )
        props_resp.raise_for_status()
        props_data = props_resp.json()

        filing_info: dict[str, dict] = {n: {} for n in batch_eids}
        for v in props_data.get("values", []):
            eid = str(v["eid"]).zfill(20)
            if eid not in filing_info:
                continue
            if v["pid"] == form_pid:
                filing_info[eid]["form_type"] = v["value"]
            elif v["pid"] == date_pid:
                filing_info[eid]["filing_date"] = v["value"]
            elif v["pid"] == acc_pid:
                filing_info[eid]["accession"] = v["value"]
            elif v["pid"] == name_pid and "name" not in filing_info[eid]:
                filing_info[eid]["name"] = v["value"]

        lines = [f"=== {co['name']} ({co['ticker']}) — Recent Filings ===\n"]
        for neid, recorded in doc_neids:
            info = filing_info.get(neid, {})
            form = info.get("form_type", "?")
            date = info.get("filing_date", recorded)
            name = info.get("name", "")
            acc = info.get("accession", "")
            line = f"  {form:8s}  {date}  {name}"
            if acc:
                line += f"  [{acc}]"
            lines.append(line)
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching filings for {co['name']}: {e}"


def get_related_entities(company: str, entity_type: str = "person") -> str:
    """Get people, organizations, or locations linked to a company.

    Args:
        company: Company name or ticker — "Apple", "Tesla", "AAPL", or "TSLA".
        entity_type: Type of linked entities. Must be "person", "organization",
            or "location".

    Returns:
        List of linked entities with names and relationship info.
    """
    co = _resolve_company(company)
    if not co:
        return f"Unknown company '{company}'. I track Apple (AAPL) and Tesla (TSLA)."

    if entity_type not in ("person", "organization", "location"):
        return f"entity_type must be 'person', 'organization', or 'location'."

    try:
        resp = elemental_client.get(
            f"/entities/{co['neid']}/linked",
            params={"entity_type": entity_type},
        )
        resp.raise_for_status()
        data = resp.json()

        entities = data.get("linked_entities", data.get("entities", []))
        if not entities:
            return f"No linked {entity_type}s found for {co['name']}."

        lines = [f"=== {co['name']} — Linked {entity_type.title()}s ===\n"]
        for ent in entities[:25]:
            name = ent.get("name", ent.get("neid", "?"))
            rel = ent.get("link_type", ent.get("relationship", ""))
            lines.append(f"  {name}" + (f"  ({rel})" if rel else ""))
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching linked entities: {e}"


def lookup_any_entity(name: str) -> str:
    """Look up any entity by name in the knowledge graph.

    Use this for entities other than Apple and Tesla (which are pre-configured).

    Args:
        name: Entity name to search for (e.g. "Microsoft", "Elon Musk").

    Returns:
        Search results with entity IDs and types.
    """
    try:
        resp = elemental_client.get(
            "/entities/lookup",
            params={"entityName": name, "maxResults": 5},
        )
        resp.raise_for_status()
        data = resp.json()
        neids = data.get("neids", [])
        names = data.get("names", [])

        if not neids:
            return f"No entities found matching '{name}'."

        lines = [f"=== Search results for '{name}' ===\n"]
        for i, neid in enumerate(neids):
            entity_name = names[i] if i < len(names) else "?"
            lines.append(f"  {entity_name}  (NEID: {neid})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error looking up '{name}': {e}"


root_agent = Agent(
    model="gemini-2.0-flash",
    name="company_analyst",
    instruction="""You are a financial analyst specializing in Apple (AAPL) and Tesla (TSLA).

You MUST use your tools to answer questions. Never guess or make up financial data.

## Known entities (no lookup needed)
- Apple Inc: NEID 00508379502570440213, ticker AAPL
- Tesla Inc: NEID 04770104648640614357, ticker TSLA

## How to answer common questions

**"What are Apple/Tesla's financials?"**
→ Call get_financials("apple") or get_financials("tesla")

**"Compare Apple and Tesla on X"**
→ Call compare_companies("total_revenue") (or net_income, total_assets, etc.)

**"Which company has more debt/revenue/assets?"**
→ Call compare_companies() with the relevant metric name:
  - Revenue → "total_revenue"
  - Profit/income → "net_income"
  - Debt/liabilities → "total_liabilities"
  - Assets → "total_assets"
  - Equity → "shareholders_equity"
  - Shares → "shares_outstanding"

**"Show recent filings"**
→ Call get_filings("apple") or get_filings("tesla")

**"Who are the officers/directors?"**
→ Call get_related_entities("apple", "person")

**"What subsidiaries does X have?"**
→ Call get_related_entities("apple", "organization")

## Formatting
- Present dollar amounts clearly: "$307B" not "307000000000"
- Always note the filing date so users know how fresh the data is
- For comparisons, use a clear side-by-side format
- When showing multiple metrics, use a table or list format""",
    tools=[
        get_financials,
        compare_companies,
        get_filings,
        get_related_entities,
        lookup_any_entity,
    ],
)
