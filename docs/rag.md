# Tutor (RAG) Routes

## `POST /api/tutor/ask` — Ask the AI Tutor

Answer questions using Hybrid RAG (vector DB → summaries → chunks → web search).

**Request Body (application/json):**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | — | Question to ask |
| `source_type` | string | Yes | web | web | pdf | url |
| `material_id` | string | No | null | Required for pdf/url sources |
| `memory_id` | string | No | null | Pass to continue conversation |

**Response:**

```json
{
  "answer": "string",
  "source": "string",
  "time_taken": 8.14,
  "memory_id": "string"
}
```

**Next.js Example:**

```ts
const res = await fetch(`${BASE_URL}/api/tutor/ask`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query,
    source_type: "web",
    material_id: null,
    memory_id: memoryId,
  }),
});
const data = await res.json();
```
