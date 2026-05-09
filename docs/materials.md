# Materials Routes

## `POST /api/materials/upload-pdf` — Upload PDF and Create Material

Upload a PDF, extract text, chunk it, and create a vector database.

**Request Body (multipart/form-data):**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file` | file | Yes | — | PDF file to process |

**Response:**

```json
{
  "material_id": "string",
  "title": "string",
  "chunks_count": 42
}
```

**Next.js Example:**

```ts
const form = new FormData();
form.append("file", file);

const res = await fetch(`${BASE_URL}/api/materials/upload-pdf`, {
  method: "POST",
  body: form,
});
const data = await res.json();
```

---

## `POST /api/materials/scrape-url` — Scrape URL and Create Material

Scrape a URL article, chunk its content, and create a vector database.

**Path Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| — | — | — | — | — |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| — | — | — | — | — |

**Request Body (application/json):**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `url` | string | Yes | — | Article URL to scrape |

**Response:**

```json
{
  "material_id": "string",
  "title": "string",
  "chunks_count": 18
}
```

**Next.js Example:**

```ts
const res = await fetch(`${BASE_URL}/api/materials/scrape-url`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ url }),
});
const data = await res.json();
```
