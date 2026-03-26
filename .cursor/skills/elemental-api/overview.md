# Elemental API Overview

The Elemental API provides access to the Lovelace Knowledge Graph through the Query Server. This document explains core concepts and guides you to the right endpoint documentation.

## Core Concepts

### Named Entity ID (NEID)

Every entity in the system has a unique identifier called a NEID. Most API calls require a NEID, so your first step is usually looking up an entity by name to get its NEID.

**Format**: 20-character numeric string with zero-padding. Example: `00416400910670863867`

When normalizing NEIDs, always pad with leading zeros to exactly 20 characters.

**Note**: The terms "eid" and "neid" are interchangeable throughout the API. Some endpoints use `neid` and others use `eid`, but they refer to the same entity identifier.

### Mention Code (MCODE)

A mention is a specific reference to an entity in an article. Each mention has a unique MCODE that links the entity, article, and context together.

**Format**: `{neid}:{artid}` with colon separator. Example: `00416400910670863867:05433395856363393596`

### Time Ranges

Most endpoints accept `start` and `end` parameters for filtering by date.

**Required format**: Full ISO 8601 with timezone.

- Correct: `2026-01-28T00:00:00Z`
- Incorrect: `2026-01-28` (missing time and timezone)

## Endpoint Categories

| File                                 | Use When You Need To...                                                                        |
| ------------------------------------ | ---------------------------------------------------------------------------------------------- |
| [entities.md](entities.md)           | Look up entities by name, get details and properties                                           |
| [find.md](find.md)                   | Search for entities by type, property values, or relationships using the expression language   |
| [sentiment.md](sentiment.md)         | Get sentiment scores and trends for an entity                                                  |
| [articles.md](articles.md)           | Get articles that mention an entity, article content, titles, summaries                        |
| [events.md](events.md)               | Find events involving an entity (mergers, lawsuits, etc.)                                      |
| [relationships.md](relationships.md) | Find connections between entities                                                              |
| [graph.md](graph.md)                 | Generate visual network graphs                                                                 |
| [server.md](server.md)               | Check server status and capabilities, as well as schema info including flavors and properties. |
| [llm.md](llm.md)                     | (Not currently available) AI-assisted queries                                                  |

## Common Workflows

### "What's the sentiment for Apple?"

1. `entities.md` → Look up "Apple" to get NEID
2. `sentiment.md` → Query sentiment with the NEID

### "How are Microsoft and OpenAI connected?"

1. `entities.md` → Look up both companies to get NEIDs
2. `relationships.md` → Query links between the two NEIDs
