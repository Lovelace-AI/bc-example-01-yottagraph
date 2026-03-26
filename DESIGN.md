# bc-example-01

## Vision

An app that periodically reads Edgar data for Apple and Tesla and stores it in our Postgres database. Also an agent that reads the data from Postgres and (along with additional info from the elemental APIs) provides an analysis of the companies.

## Status

Core features implemented. Ready for deployment.

## Modules

### Dashboard (`pages/index.vue`)

Side-by-side overview of Apple and Tesla. Shows latest financial metrics (revenue, net income, assets, liabilities, equity, shares outstanding), filing counts, and last sync time. Includes a Sync Now button to trigger EDGAR data fetch.

### Company Detail (`pages/company/[ticker].vue`)

Detailed view per company with three tabs:

- **Financials** — sortable table of historical financial data by filing date
- **Filings** — SEC filing list (form type, date, accession number)
- **Trend Chart** — Chart.js line chart for revenue, net income, and total assets over time

### Analyst Chat (`pages/chat.vue`)

Chat interface connected to deployed ADK agents via the Portal Gateway. Supports agent selection, streaming responses, and sample prompts for common analysis questions.

### EDGAR Sync (`server/api/edgar/`)

Server routes that fetch data from the Lovelace Elemental API and store it in Neon Postgres:

- `POST /api/edgar/setup` — creates `companies`, `filings`, `financials` tables
- `POST /api/edgar/sync` — fetches EDGAR data for AAPL and TSLA, stores in Postgres
- `GET /api/edgar/companies` — returns tracked companies with latest metrics
- `GET /api/edgar/filings?ticker=AAPL` — returns filings for a company
- `GET /api/edgar/financials?ticker=AAPL` — returns financial history

Vercel cron job runs sync daily at 6 AM UTC (`vercel.json`).

### Company Analyst Agent (`agents/company_analyst/`)

Python ADK agent with tools for:

- Knowledge graph schema discovery
- Entity lookup and property retrieval (financial metrics with historical data)
- Entity search via expression language
- Linked entity exploration (officers, subsidiaries, related orgs)

Focused on Apple and Tesla analysis but can query any entity in the graph.

### Data Architecture

| Store                        | Usage                                                      |
| ---------------------------- | ---------------------------------------------------------- |
| Elemental API (Query Server) | Source of truth for EDGAR data, entity relationships, news |
| Neon Postgres                | Synced financial snapshots and filing metadata             |
| KV (Upstash Redis)           | User preferences                                           |

### Navigation

Permanent sidebar: Dashboard, Apple, Tesla, Analyst Chat.
