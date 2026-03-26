# Relationships

Relationships (also called "links") represent connections between entities in the Knowledge Graph. These connections are derived from articles.

## When to Use

- You want to find entities connected to a given entity
- You need to understand how two entities are related
- You're exploring a network of connections (e.g., "Who is connected to this person?")
- You need link counts or relationship strength between entities

## Key Concepts

- **Linked Entities**: Other entities that have a relationship with a given entity
- **Link Strength**: Represents the significance of the relationship between two entities
- **Link Counts**: Number of connections between entity pairs, useful for measuring relationship strength
- **Relationship Types**: Common types include:
    - `competes_with`
    - `compares_to`
    - `customer_of`
    - `partnered_with`
    - `trades_with`
    - `invests_in`
    - `is_related_to`
    - `sues`
    - `provides_support_to`

## Tips

- Relationships are bidirectional—if A links to B, B links to A
- High link counts indicate stronger or more frequent connections in the news
- Use with graph endpoints to visualize relationship networks
- **`entity_type` filter limitation**: see the Guidance note on "Get linked entities" below — only three entity types are supported

<!-- BEGIN GENERATED CONTENT -->

## Endpoints

### Get linked entities

`GET /entities/{source_neid}/linked`

Get list of entities linked to a source entity, optionally filtered by entity type and link type

#### Parameters

| Name        | Type     | Required | Description              |
| ----------- | -------- | -------- | ------------------------ |
| source_neid | string   | yes      | Source entity NEID       |
| entity_type | string[] | no       | Filter by entity type(s) |
| link_type   | string[] | no       | Filter by link type(s)   |

#### Responses

| Status | Description                                               |
| ------ | --------------------------------------------------------- |
| 200    | List of linked entity NEIDs (`GetLinkedEntitiesResponse`) |
| 400    | Invalid parameters (`Error`)                              |
| 404    | Source entity not found (`Error`)                         |
| 500    | Internal server error (`Error`)                           |

#### Example

**Request:**

```
GET /entities/00416400910670863867/linked
```

**Response:**

```json
{ "entities": ["00416400910670863867"] }
```

---

### Get links between entities

`GET /entities/{source_neid}/links/{target_neid}`

Get list of links between source and target entities, optionally filtered by link type

#### Parameters

| Name             | Type     | Required | Description                         |
| ---------------- | -------- | -------- | ----------------------------------- |
| source_neid      | string   | yes      | Source entity NEID                  |
| target_neid      | string   | yes      | Target entity NEID                  |
| link_type        | string[] | no       | Filter by link type(s)              |
| include_mentions | boolean  | no       | Include mention details in response |
| include_articles | boolean  | no       | Include article details in response |

#### Responses

| Status | Description                                 |
| ------ | ------------------------------------------- |
| 200    | List of entity links (`GetLinksResponse`)   |
| 400    | Invalid parameters (`Error`)                |
| 404    | Source or target entity not found (`Error`) |
| 500    | Internal server error (`Error`)             |

#### Example

**Request:**

```
GET /entities/00416400910670863867/links/04358848009837283240
```

**Response:**

```json
{ "links": [] }
```

---

### Get graph layout

`GET /graph/{center_neid}/layout`

Get nodes and edges layout data for visualizing a relationship graph. Response is cached for 5 minutes.

#### Guidance

Only use this endpoint if you care about graph-specific properties. Otherwise it is faster to use /entities/{source_neid}/links/{target_neid}. This should always be called with a non-empty list of neids. A typical pattern is to call /graph/{center_neid}/neighborhood and then use the returned NEIDs to call this endpoint.

#### Parameters

| Name        | Type     | Required | Description                                  |
| ----------- | -------- | -------- | -------------------------------------------- |
| center_neid | string   | yes      | Center entity NEID                           |
| neid        | string[] | no       | Additional entity NEIDs to include in layout |
| borderMinX  | number   | no       | Minimum X border for layout                  |
| borderMinY  | number   | no       | Minimum Y border for layout                  |
| borderMaxX  | number   | no       | Maximum X border for layout                  |
| borderMaxY  | number   | no       | Maximum Y border for layout                  |

#### Responses

| Status | Description                                               |
| ------ | --------------------------------------------------------- |
| 200    | Graph layout with nodes and edges (`GraphLayoutResponse`) |
| 400    | Invalid parameters (`Error`)                              |
| 500    | Internal server error (`Error`)                           |

#### Example

**Request:**

```
GET /graph/00416400910670863867/layout?neid=04358848009837283240
```

**Response:**

```json
{
    "nodes": [
        {
            "neid": "00416400910670863867",
            "label": "organization|Apple|nationality: us...",
            "isCentralNode": true,
            "x": -333.33,
            "y": -200,
            "width": 666.67,
            "height": 266.67
        }
    ],
    "edges": [
        {
            "source": "00416400910670863867",
            "target": "04358848009837283240",
            "label": "competes_with",
            "path": [
                { "X": 0, "Y": 0 },
                { "X": 0, "Y": 66.67 }
            ],
            "article_ids": ["02861951941133789623"],
            "snippets": ["Apple and Google are mentioned as companies..."],
            "weight": 0.0267
        }
    ]
}
```

---

### Get graph neighborhood

`GET /graph/{center_neid}/neighborhood`

Get list of neighboring entities in the relationship graph, optionally filtered by entity type. Response is cached for 5 minutes.

#### Guidance

Only use this endpoint if you care about graph-specific properties. Otherwise it is faster to use /entities/{source_neid}/linked. Response includes the center entity itself in the results with a weight of 1.0. The 'neighbors' and 'weights' arrays are parallel (same indices correspond).

#### Parameters

| Name        | Type     | Required | Description                           |
| ----------- | -------- | -------- | ------------------------------------- |
| center_neid | string   | yes      | Center entity NEID                    |
| size        | integer  | no       | Maximum number of neighbors to return |
| type        | string[] | no       | Filter by entity type(s)              |

#### Responses

| Status | Description                                               |
| ------ | --------------------------------------------------------- |
| 200    | Neighbors and their weights (`GraphNeighborhoodResponse`) |
| 400    | Invalid parameters (`Error`)                              |
| 404    | Center entity not found (`Error`)                         |
| 500    | Internal server error (`Error`)                           |

#### Example

**Request:**

```
GET /graph/00416400910670863867/neighborhood?size=5
```

**Response:**

```json
{
    "neighbors": ["00416400910670863867", "04358848009837283240", "00315863961550087877"],
    "weights": [1, 0.0267, 0.0167]
}
```

---

### Get link counts between entities

`GET /graph/{source_neid}/links/{target_neid}/counts`

Get counts of links between source and target entities over time

#### Guidance

Only use this endpoint if you care about graph-specific properties. Otherwise it is faster to use /entities/{source_neid}/links/{target_neid}. Returns link_counts object with relationship types as keys. Values are arrays of timestamps in Excel/OLE serial date format (days since 1899-12-30). Example: 46019.64453125 = 2025-12-28 15:28:07 UTC. The count for each relationship type is the array length (number of observations).

#### Parameters

| Name        | Type   | Required | Description        |
| ----------- | ------ | -------- | ------------------ |
| source_neid | string | yes      | Source entity NEID |
| target_neid | string | yes      | Target entity NEID |

#### Responses

| Status | Description                                   |
| ------ | --------------------------------------------- |
| 200    | Link counts by type (`GetLinkCountsResponse`) |
| 400    | Invalid parameters (`Error`)                  |
| 500    | Internal server error (`Error`)               |

#### Example

**Request:**

```
GET /graph/00416400910670863867/links/04358848009837283240/counts
```

**Response:**

```json
{
    "link_counts": {
        "compares_to": [46019.64453125, 45999.3515625],
        "competes_with": [45847.5625, 45850.60546875],
        "customer_of": [45836.9296875],
        "partnered_with": [],
        "trades_with": []
    }
}
```

## Types

### EntityLink

A link between two entities

| Field       | Type     | Description                                       |
| ----------- | -------- | ------------------------------------------------- |
| article_ids | string[] | Article IDs where this link was found             |
| recorded_at | string   | Time when the link was recorded @Format date-time |
| source      | string   | Source entity NEID                                |
| target      | string   | Target entity NEID                                |
| type        | string   | Type of link/relationship                         |

### GetLinkCountsResponse

Response containing link counts between entities

| Field       | Type   | Description                      |
| ----------- | ------ | -------------------------------- |
| link_counts | object | Map of link type to count values |

### GetLinkedEntitiesResponse

Response containing linked entities

| Field    | Type     | Description                 |
| -------- | -------- | --------------------------- |
| entities | string[] | List of linked entity NEIDs |

### GetLinksResponse

Response containing links between entities

| Field    | Type              | Description                                                        |
| -------- | ----------------- | ------------------------------------------------------------------ |
| articles | `ArticleDetail`[] | Articles tied to the returned links (only included when requested) |
| links    | `EntityLink`[]    | List of entity links                                               |
| mentions | `MentionDetail`[] | Mentions tied to the returned links (only included when requested) |

### GraphNeighborhoodResponse

Response containing neighbors of an entity in the relationship graph

| Field     | Type     | Description                                                      |
| --------- | -------- | ---------------------------------------------------------------- |
| neighbors | string[] | List of neighbor NEIDs                                           |
| weights   | number[] | Weights corresponding to each neighbor (same order as neighbors) |

### LinkedExpression

| Field      | Type     | Description |
| ---------- | -------- | ----------- |
| **linked** | `Linked` |             |

### Linked

| Field        | Type      | Description                                                                                                                                                                             |
| ------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **distance** | integer   | Maximum relationship distance to traverse                                                                                                                                               |
| pids         | integer[] | Property identifiers defining the relationship types to follow                                                                                                                          |
| to_entity    | string    | Target entity ID for relationship traversal                                                                                                                                             |
| direction    | string    | Direction of relationship traversal. 'outgoing' (default) follows subject->value edges, 'incoming' follows value->subject (reverse) edges, 'both' unions outgoing and incoming results. |

<!-- END GENERATED CONTENT -->
