# Articles & Mentions

Articles are one significant source of data for the Knowledge Graph. A **mention** is a specific reference to an entity within an article, capturing the context and sentiment of that reference.

## When to Use

- You need to find news coverage about an entity
- You want mention counts or volume over time
- You have a specific article ID (ARTID) or mention code (MCODE) and need full details
- You want to read the actual text or summary of an article
- You need article metadata: publication name, date, URL, trustworthiness scores

## Key Concepts

- **ARTID**: Unique identifier for each article.
    - Format: 20-character numeric string (same format as NEIDs)
    - Example: `05433395856363393596`
- **MCODE**: A unique identifier for each mention, linking entity + article + context.
    - Format: `{neid}:{artid}` with colon separator
    - Example: `00416400910670863867:05433395856363393596`
- **Mention Detail**: Includes the snippet, publication, sentiment, and other metadata
- **Mention Counts**: Aggregated counts over time buckets, useful for tracking media attention
- **Article Detail**: Full metadata including title, summary, publication info, and scores
- **Article Text**: The actual content of the article (when available)

## Important Limitations

⚠️ **Volume Warning**: A single entity may have tens of thousands of associated articles. Avoid querying all articles for an entity over long time periods.

**Recommended approach:**

1. Start with mention counts to understand volume
2. Use mention endpoints to identify specific mentions of interest
3. Then retrieve full article details only for those specific articles

## Tips

- Start with mention counts to understand volume, then drill into specific mentions
- Filter by time range to avoid overwhelming results for high-profile entities
- Use neighborhood mentions to see what else was mentioned alongside your target entity
- Article text may not be available for all articles (depends on licensing)
- Use trustworthiness and page rank scores to assess source quality

<!-- BEGIN GENERATED CONTENT -->

## Endpoints

### Get article detail

`GET /articles/{artid}`

Get detailed information about an article by its ID. Response is cached for 1 hour (articles are immutable).

#### Guidance

Response is wrapped in a 'detail' container object. Access article data via response.detail.

#### Parameters

| Name  | Type   | Required | Description |
| ----- | ------ | -------- | ----------- |
| artid | string | yes      | Article ID  |

#### Responses

| Status | Description                           |
| ------ | ------------------------------------- |
| 200    | Article detail (`GetArticleResponse`) |
| 400    | Invalid ARTID (`Error`)               |
| 404    | Article not found (`Error`)           |
| 500    | Internal server error (`Error`)       |

#### Example

**Request:**

```
GET /articles/05433395856363393596
```

**Response:**

```json
{
    "detail": {
        "artid": "05433395856363393596",
        "publication_date": "2026-01-28T15:56:47Z",
        "title": "Apple's Cook says he's 'heartbroken' by Minneapolis events...",
        "summary": "The article details two fatal shootings by federal agents...",
        "batch": "7f302ee6808d7c45a09aed07c93ec785",
        "source": "7f302ee6808d7c45a09aed07c93ec785",
        "url": "https://www.cnbc.com/2026/01/28/...",
        "mentions": [{ "neid": "00315863961550087877", "artid": "05433395856363393596" }],
        "topics": [],
        "events": ["00526686651102446795", "01090525413205193094"],
        "publication_name": "cnbc.com",
        "publication_home_url": "http://www.cnbc.com",
        "trustworthiness": 0.664,
        "original_publication_name": "CNBC",
        "tone": "neutral",
        "title_factuality": "accurate",
        "tone_objectivity_score": 0.533,
        "title_factuality_score": 7.133,
        "syndication_score": 1
    }
}
```

---

### Get article text

`GET /articles/{artid}/text`

Get the full text content of an article by its ID. Response is cached for 10 minutes.

#### Guidance

This endpoint returns plain text, NOT JSON. Parse the response as text, not as a JSON object.

#### Parameters

| Name  | Type   | Required | Description |
| ----- | ------ | -------- | ----------- |
| artid | string | yes      | Article ID  |

#### Responses

| Status | Description                     |
| ------ | ------------------------------- |
| 200    | Article text                    |
| 400    | Invalid ARTID (`Error`)         |
| 500    | Internal server error (`Error`) |

#### Example

**Request:**

```
GET /articles/05433395856363393596/text
```

**Response:**

```
Apple CEO Tim Cook said he was "heartbroken" by the situation in Minneapolis...
```

---

### Get mentions for entities

`GET /mentions/lookup`

Get list of mention codes (MCODEs) for named entities in a neighborhood within a time interval. Response is cached for 5 minutes.

#### Parameters

| Name           | Type     | Required | Description                            |
| -------------- | -------- | -------- | -------------------------------------- |
| interval_start | string   | yes      | Start time of interval (RFC3339)       |
| interval_end   | string   | yes      | End time of interval (RFC3339)         |
| neid           | string[] | yes      | Named Entity ID(s) in the neighborhood |

#### Responses

| Status | Description                                   |
| ------ | --------------------------------------------- |
| 200    | List of mention codes (`GetMentionsResponse`) |
| 400    | Invalid parameters (`Error`)                  |
| 500    | Internal server error (`Error`)               |

#### Example

**Request:**

```
GET /mentions/lookup?interval_start=2026-01-01T00:00:00Z&interval_end=2026-02-01T00:00:00Z&neid=00416400910670863867
```

**Response:**

```json
{
    "mcodes": [
        { "neid": "00416400910670863867", "artid": "05433395856363393596" },
        { "neid": "00416400910670863867", "artid": "02706389331155211812" }
    ]
}
```

---

### Get mention counts over time

`GET /mentions/lookup/counts`

Get bucketed counts of mentions for entities in a neighborhood within a time interval

#### Parameters

| Name           | Type     | Required | Description                            |
| -------------- | -------- | -------- | -------------------------------------- |
| interval_start | string   | yes      | Start time of interval (RFC3339)       |
| interval_end   | string   | yes      | End time of interval (RFC3339)         |
| neid           | string[] | yes      | Named Entity ID(s) in the neighborhood |
| numBuckets     | integer  | no       | Number of time buckets                 |

#### Responses

| Status | Description                                          |
| ------ | ---------------------------------------------------- |
| 200    | Bucketed mention counts (`GetMentionCountsResponse`) |
| 400    | Invalid parameters (`Error`)                         |
| 500    | Internal server error (`Error`)                      |

#### Example

**Request:**

```
GET /mentions/lookup/counts?interval_start=2026-01-15T00:00:00Z&interval_end=2026-01-20T00:00:00Z&neid=00416400910670863867&numBuckets=5
```

**Response:**

```json
{
    "buckets": [
        { "start": "2026-01-15T00:00:00Z", "width_hours": 24, "count": 51 },
        { "start": "2026-01-16T00:00:00Z", "width_hours": 24, "count": 28 }
    ]
}
```

---

### Get mention details for a neighborhood

`GET /mentions/lookup/detail`

Get detailed information about all mentions for entities in a neighborhood within a time interval. Response is cached for 15 minutes.

#### Parameters

| Name           | Type     | Required | Description                            |
| -------------- | -------- | -------- | -------------------------------------- |
| interval_start | string   | yes      | Start time of interval (RFC3339)       |
| interval_end   | string   | yes      | End time of interval (RFC3339)         |
| neid           | string[] | yes      | Named Entity ID(s) in the neighborhood |

#### Responses

| Status | Description                                                |
| ------ | ---------------------------------------------------------- |
| 200    | List of mention details (`GetMentionLookupDetailResponse`) |
| 400    | Invalid parameters (`Error`)                               |
| 500    | Internal server error (`Error`)                            |

#### Example

**Request:**

```
GET /mentions/lookup/detail?interval_start=2026-01-28T00:00:00Z&interval_end=2026-01-29T00:00:00Z&neid=00416400910670863867
```

**Response:**

```json
{
    "details": [
        {
            "neid": "00416400910670863867",
            "artid": "06794762728091918955",
            "publication_date": "2026-01-28T14:01:17Z",
            "snippet": "...stiff competition from other major players such as YouTube and Apple...",
            "sentiment": 0,
            "explanation": "Apple is mentioned as a competitor in the music-streaming market...",
            "topics": [],
            "trustworthiness": 0.508,
            "original_publication_name": "Spotify",
            "tone": "Neutral",
            "title_factuality": "True",
            "tone_objectivity_score": 0.563,
            "title_factuality_score": 3.889,
            "events": ["06942391178010057368"]
        }
    ]
}
```

---

### Get mention detail

`GET /mentions/{mcode}/detail`

Get detailed information about a specific mention by its MCODE. Response is cached for 15 minutes.

#### Guidance

Response is wrapped in a 'detail' container object. Access mention data via response.detail.

#### Parameters

| Name  | Type   | Required | Description                       |
| ----- | ------ | -------- | --------------------------------- |
| mcode | string | yes      | Mention code in format NEID:ARTID |

#### Responses

| Status | Description                                 |
| ------ | ------------------------------------------- |
| 200    | Mention detail (`GetMentionDetailResponse`) |
| 400    | Invalid MCODE format (`Error`)              |
| 404    | Mention not found (`Error`)                 |
| 500    | Internal server error (`Error`)             |

#### Example

**Request:**

```
GET /mentions/00416400910670863867:05433395856363393596/detail
```

**Response:**

```json
{
    "detail": {
        "neid": "00416400910670863867",
        "artid": "05433395856363393596",
        "publication_date": "2026-01-28T15:56:47Z",
        "snippet": "Apple CEO Tim Cook said he was 'heartbroken'...",
        "sentiment": -0.75,
        "explanation": "CEO Tim Cook expressed heartbreak...",
        "topics": [],
        "trustworthiness": 0.664,
        "original_publication_name": "CNBC",
        "tone": "neutral",
        "title_factuality": "accurate",
        "tone_objectivity_score": 0.533,
        "title_factuality_score": 7.133,
        "events": ["07189853443333370710", "07880710486873721498"]
    }
}
```

## Types

### ArticleDetail

The article detail

| Field                     | Type             | Description                                                                |
| ------------------------- | ---------------- | -------------------------------------------------------------------------- |
| artid                     | string           | Article ID                                                                 |
| batch                     | string           | Processing batch identifier                                                |
| events                    | string[]         | Event IDs mentioned in this article                                        |
| mentions                  | `Mcode`[]        | List of entity mentions in article                                         |
| moz_rank_score            | number           | Publisher's Moz rank value (0 to 1) @Minimum 0 @Maximum 1                  |
| original_publication_name | string           | Original publication name when known (e.g., when article is syndicated)    |
| page_rank_score           | number           | Publisher's page rank value (0 to 1) @Minimum 0 @Maximum 1                 |
| publication_date          | string           | Publication date of the article @Format date-time                          |
| publication_home_url      | string           | Home URL of the publication in which the article was published @Format uri |
| publication_name          | string           | Name of the publication in which the article was published                 |
| source                    | string           | Article source identifier                                                  |
| summary                   | string           | Article summary                                                            |
| syndication_score         | integer          | Syndication score indicating article distribution                          |
| title                     | string           | Article title                                                              |
| title_factuality          | string           | Article title factuality classification                                    |
| title_factuality_score    | number           | Publisher's title factuality score (0 to 1) @Minimum 0 @Maximum 1          |
| tone                      | string           | Article tone classification                                                |
| tone_objectivity_score    | number           | Publisher's tone objectivity score (0 to 1) @Minimum 0 @Maximum 1          |
| topics                    | `ArticleTopic`[] | Topics associated with this article                                        |
| trustworthiness           | number           | Trustworthiness score (0 to 1) @Minimum 0 @Maximum 1                       |
| url                       | string           | Original article URL @Format uri                                           |

### GetArticleResponse

Response containing detailed information about an article

| Field  | Type            | Description |
| ------ | --------------- | ----------- |
| detail | `ArticleDetail` |             |

### GetMentionCountsResponse

Response containing bucketed mention counts over time

| Field   | Type       | Description                      |
| ------- | ---------- | -------------------------------- |
| buckets | `Bucket`[] | Time buckets with mention counts |

### GetMentionDetailResponse

Response containing detailed information about a mention

| Field  | Type            | Description |
| ------ | --------------- | ----------- |
| detail | `MentionDetail` |             |

### GetMentionLookupDetailResponse

Response containing detailed information about multiple mentions

| Field   | Type              | Description             |
| ------- | ----------------- | ----------------------- |
| details | `MentionDetail`[] | List of mention details |

### GetMentionsResponse

Response containing mention codes for a lookup query

| Field  | Type      | Description                               |
| ------ | --------- | ----------------------------------------- |
| mcodes | `Mcode`[] | List of mention codes (NEID, ARTID pairs) |

### Mcode

A tuple of (NEID, ARTID) representing one or more mentions of a Named Entity in an Article

| Field | Type   | Description     |
| ----- | ------ | --------------- |
| artid | string | Article ID      |
| neid  | string | Named Entity ID |

### MentionDetail

The mention detail

| Field                     | Type             | Description                                                             |
| ------------------------- | ---------------- | ----------------------------------------------------------------------- |
| artid                     | string           | Article ID                                                              |
| events                    | string[]         | Event IDs that this mention is associated with                          |
| explanation               | string           | Explanation of sentiment analysis                                       |
| moz_rank_score            | number           | Publisher's Moz rank value (0 to 1) @Minimum 0 @Maximum 1               |
| neid                      | string           | Named Entity ID                                                         |
| original_publication_name | string           | Original publication name when known (e.g., when article is syndicated) |
| other_neid                | string           | NEID of the other entity in a relationship mention                      |
| other_relation_type       | string           | Type of relationship with the other entity                              |
| page_rank_score           | number           | Publisher's page rank value (0 to 1) @Minimum 0 @Maximum 1              |
| publication_date          | string           | Publication date of the article @Format date-time                       |
| sentiment                 | number           | Sentiment score for the mention (-1 to 1) @Minimum -1 @Maximum 1        |
| snippet                   | string           | Text snippet containing the mention                                     |
| title_factuality          | string           | Article title factuality classification                                 |
| title_factuality_score    | number           | Publisher's title factuality score (0 to 1) @Minimum 0 @Maximum 1       |
| tone                      | string           | Article tone classification                                             |
| tone_objectivity_score    | number           | Publisher's tone objectivity score (0 to 1) @Minimum 0 @Maximum 1       |
| topics                    | `ArticleTopic`[] | Topics associated with the article                                      |
| trustworthiness           | number           | Trustworthiness score (0 to 1) @Minimum 0 @Maximum 1                    |

<!-- END GENERATED CONTENT -->
