# Sentiment

Sentiment analysis measures how positively or negatively an entity is portrayed in news coverage. The API provides both daily aggregate scores and scores for individual articles.

## When to Use

- You want to know if news coverage about an entity is positive or negative
- You need sentiment trends over time (e.g., "How has sentiment changed this month?")
- You're comparing sentiment between entities or time periods

## Key Concepts

- **Sentiment Score**: Ranges from -1 (very negative) to +1 (very positive), with 0 being neutral.
    - Individual article/mention scores are discrete values: `-1`, `-0.75`, `-0.5`, `0`, `0.5`, `0.75`, `1`
    - Daily aggregate scores can be any value between -1 and 1 (continuous)
- **Entity-level vs. Mention-level**: Aggregate sentiment for an entity vs. sentiment of a specific mention

## Tips

- Sentiment without a time range returns recent data; always specify dates for historical analysis
- High mention volume with neutral sentiment may indicate routine coverage
- Sudden sentiment shifts often correlate with specific events

<!-- BEGIN GENERATED CONTENT -->

## Endpoints

### Get entity sentiment data

`GET /graph/{neid}/sentiment`

Get sentiment analysis data for a named entity including scores, timestamps, and daily averages. Response is cached for 5 minutes.

#### Guidance

Response is wrapped in a 'sentiment' container object. The sentiment_scores field is a flat array of numbers (not timestamped objects). The time interval for the scores is provided separately in time_interval.start and time_interval.end.

#### Parameters

| Name | Type   | Required | Description     |
| ---- | ------ | -------- | --------------- |
| neid | string | yes      | Named Entity ID |

#### Responses

| Status | Description                                                       |
| ------ | ----------------------------------------------------------------- |
| 200    | Sentiment data for the entity (`GetNamedEntitySentimentResponse`) |
| 400    | Invalid NEID (`Error`)                                            |
| 404    | Entity not found (`Error`)                                        |
| 500    | Internal server error (`Error`)                                   |

#### Example

**Request:**

```
GET /graph/00416400910670863867/sentiment
```

**Response:**

```json
{
    "sentiment": {
        "neid": "00416400910670863867",
        "time_interval": { "start": "2026-01-04T03:02:25.384Z", "end": "2026-02-03T03:02:25.384Z" },
        "num_mentions": 28662,
        "sentiment_scores": [0.5, 0.5, 0.5, 0, 0.5, -0.5, 1]
    }
}
```

## Types

### GetNamedEntitySentimentResponse

Response containing sentiment data for a named entity

| Field     | Type                   | Description |
| --------- | ---------------------- | ----------- |
| sentiment | `NamedEntitySentiment` |             |

### NamedEntitySentiment

The sentiment data

| Field                               | Type           | Description                                                                             |
| ----------------------------------- | -------------- | --------------------------------------------------------------------------------------- |
| daily_timestamps                    | string[]       | Timestamps associated with each daily sentiment trend                                   |
| direct_sentiment_daily_averages     | number[]       | The average direct sentiment score for the entity for each day in the time interval     |
| neid                                | string         | Named Entity ID                                                                         |
| num_mentions                        | integer        | Number of times the entity has been directly mentioned in an article                    |
| propagated_sentiment_daily_averages | number[]       | The average propagated sentiment score for the entity for each day in the time interval |
| sentiment_article_nindexes          | string[]       | Nindexes of the articles that correspond to each direct sentiment score                 |
| sentiment_scores                    | number[]       | All direct sentiment scores for the entity                                              |
| sentiment_timestamps                | string[]       | Timestamps associated with each direct sentiment score                                  |
| time_interval                       | `TimeInterval` |                                                                                         |

<!-- END GENERATED CONTENT -->
