# Events

Events are significant occurrences involving entities: mergers, acquisitions, lawsuits, executive changes, product launches, and other newsworthy happenings. Events are extracted from article content and link multiple entities and articles together.

## When to Use

- You want to know what happened to/with an entity (not just mentions)
- You want to see how different articles reference the same event(s), and understand that many articles may duplicate information about the same event(s).
- You want to see what entities participated in an event, and what their roles were.

## Key Concepts

- **Event ID (EVEID)**: Unique identifier for each event.
    - Format: 20-character numeric string (same format as NEIDs)
    - Example: `08640179941787350436`
- **Event Roles**: Entities participate in events with roles (e.g., acquirer, target, plaintiff)
- **Event Summary**: Brief description of what occurred
- **Event Date**: When the event happened (may differ from article publication date)

## Tips

- Multiple articles may reference the same event
- Check entity roles to understand the nature of involvement

<!-- BEGIN GENERATED CONTENT -->

## Endpoints

### Get events for an entity

`GET /events/lookup`

Get list of event IDs (EVEIDs) where an entity participates within a time interval. Response is cached for 5 minutes.

#### Guidance

Event IDs returned may not all be immediately retrievable via /events/{eveid}. Some events may return 404 due to event processing timing or data availability. Handle 404 responses gracefully.

#### Parameters

| Name           | Type   | Required | Description                      |
| -------------- | ------ | -------- | -------------------------------- |
| interval_start | string | yes      | Start time of interval (RFC3339) |
| interval_end   | string | yes      | End time of interval (RFC3339)   |
| neid           | string | yes      | Named Entity ID                  |

#### Responses

| Status | Description                                      |
| ------ | ------------------------------------------------ |
| 200    | List of event IDs (`GetEventsForEntityResponse`) |
| 400    | Invalid parameters (`Error`)                     |
| 500    | Internal server error (`Error`)                  |

#### Example

**Request:**

```
GET /events/lookup?interval_start=2026-01-28T00:00:00Z&interval_end=2026-01-29T00:00:00Z&neid=00416400910670863867
```

**Response:**

```json
{ "event_ids": ["07880710486873721498", "07189853443333370710", "01188063638449369172"] }
```

---

### Get event detail

`GET /events/{eveid}`

Get detailed information about an event by its ID. Response is cached for 15 minutes.

#### Guidance

Response is wrapped in a 'detail' container object. Access event data via response.detail.

#### Parameters

| Name  | Type   | Required | Description |
| ----- | ------ | -------- | ----------- |
| eveid | string | yes      | Event ID    |

#### Responses

| Status | Description                       |
| ------ | --------------------------------- |
| 200    | Event detail (`GetEventResponse`) |
| 400    | Invalid EVEID (`Error`)           |
| 404    | Event not found (`Error`)         |
| 500    | Internal server error (`Error`)   |

#### Example

**Request:**

```
GET /events/08640179941787350436
```

**Response:**

```json
{
    "detail": {
        "eveid": "08640179941787350436",
        "name": "event|Apple plans to release a foldable device...|2026",
        "date": "2026",
        "description": "The new design and engineering changes in the iPhone Air could pave the way...",
        "category": "Product Development",
        "likelihood": "Medium",
        "severity": 0,
        "speculative": false,
        "participants": [
            {
                "neid": "00416400910670863867",
                "sentiment": 0.5,
                "explanation": "The launch of new products...",
                "role": "company",
                "snippet": "Apple is gearing up for the most extensive refresh...",
                "artid": "07521758285625650094"
            }
        ]
    }
}
```

## Types

### EventDetail

The event detail

| Field        | Type                 | Description                            |
| ------------ | -------------------- | -------------------------------------- |
| artids       | string[]             | Article IDs where this event was found |
| category     | string               | Category of the event                  |
| date         | string               | Date of the event                      |
| description  | string               | Description of the event               |
| eveid        | string               | Event ID                               |
| likelihood   | string               | Likelihood assessment of the event     |
| name         | string               | Name of the event                      |
| participants | `EventParticipant`[] | Participants in the event              |
| severity     | integer              | Severity level of the event            |
| speculative  | boolean              | Whether the event is speculative       |

### GetEventResponse

Response containing detailed information about an event

| Field  | Type          | Description |
| ------ | ------------- | ----------- |
| detail | `EventDetail` |             |

### GetEventsForEntityResponse

Response containing event IDs for an entity

| Field     | Type     | Description       |
| --------- | -------- | ----------------- |
| event_ids | string[] | List of event IDs |

<!-- END GENERATED CONTENT -->
