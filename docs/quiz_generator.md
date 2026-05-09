# Quiz Generator Routes

## `POST /api/quiz/generate` — Generate Quiz

Generate an educational quiz (MCQ + True/False) from web search, PDF material, or URL article.


**Request Body (application/json):**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `difficulty` | string | Yes | Medium | Easy | Medium | Hard |
| `mcq_count` | int | Yes | 4 | 1–20 |
| `tf_count` | int | Yes | 3 | 1–20 |
| `source_type` | string | Yes | web | web | pdf | url |
| `material_id` | string | No | null | Required for pdf/url sources |
| `topic` | string | No | null | Required for web source |

**Response:**

```json
{
  "quiz": {
    "quiz_type": "string",
    "difficulty": "string",
    "mcq_count": 4,
    "tf_count": 3,
    "mcq": [],
    "tf": []
  }
}
```

**Next.js Example:**

```ts
const res = await fetch(`${BASE_URL}/api/quiz/generate`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    difficulty: "Medium",
    mcq_count: 4,
    tf_count: 3,
    source_type: "web",
    topic,
  }),
});
const data = await res.json();
```
