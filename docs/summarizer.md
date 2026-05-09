# Summarizer Routes

## `POST /api/materials/summarize` — Generate Material Summary

Generate a structured summary for previously uploaded material (PDF or URL).

**Request Body (application/json):**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `material_id` | string | Yes | — | Material ID from upload/scrape |

**Response:**

```json
{
  "summary": "string",
  "time_taken": 5.32
}
```

**Next.js Example:**

```ts
const res = await fetch(`${BASE_URL}/api/materials/summarize`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ material_id: materialId }),
});
const data = await res.json();
```
