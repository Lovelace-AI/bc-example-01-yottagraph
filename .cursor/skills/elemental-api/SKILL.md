---
name: elemental-api
description: Query the Elemental API for entity discovery, search, and metadata. Use with the Lovelace News Query Server.
---

# Elemental API

This skill provides documentation for the Lovelace Elemental API, the primary interface for querying the Lovelace Knowledge Graph.

## When to Use This Skill

Use this skill when you need to:

- Look up entities (companies, people, organizations) by name or ID
- Get sentiment analysis for entities over time
- Find news mentions and articles about entities
- Explore relationships and connections between entities
- Retrieve events involving specific entities
- Build knowledge graphs of entity networks

## Quick Start

1. **Find an entity**: Use `entities.md` to look up a company or person by name and get their NEID (Named Entity ID)
2. **Get information**: Use the NEID to query sentiment, mentions, relationships, or events
3. **Dive deeper**: Retrieve full article details or explore connected entities

## Files in This Skill

See [overview.md](overview.md) for descriptions of each endpoint category:

- `entities.md` - Entity search, details, and properties
- `find.md` - Expression language for searching entities by type, property values, and relationships
- `schema.md` - Data model: entity types (flavors), properties, and schema endpoints
- `sentiment.md` - Sentiment analysis
- `articles.md` - Articles mentioning entities and full article content
- `events.md` - Events involving entities
- `relationships.md` - Entity connections
- `graph.md` - Visual graph generation
- `server.md` - Server status and health
