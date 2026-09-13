# Bots Backend — API Reference

Base URL: `http://localhost:8000` (adjust for your deployment environment)

CORS is enabled for all origins — no proxy required during development.

---

## Endpoints

### GET /customers

Returns the list of all available customers.

**Request**

No parameters required.

```
GET /customers
```

**Response**

`200 OK` — JSON array of customer objects.

```json
[
  { "id": "fci",      "name": "Foam Crafts India" },
  { "id": "proficio", "name": "Proficio Software Solutions" }
]
```

| Field  | Type   | Description                                             |
|--------|--------|---------------------------------------------------------|
| `id`   | string | Unique customer identifier. Use this as `company_id` in `/chat`. |
| `name` | string | Human-readable company name for display.               |

**Usage pattern**

Call this endpoint on app load to populate a customer selector. Store `id` values for subsequent chat requests.

```js
const res = await fetch('/customers');
const customers = await res.json();
// customers[0] → { id: "fci", name: "Foam Crafts India" }
```

---

### GET /chat

Sends a query to the AI assistant in the context of a specific customer. Returns the response as a **plain-text stream** (chunked transfer encoding).

**Request**

| Query param  | Type   | Required | Description                                    |
|--------------|--------|----------|------------------------------------------------|
| `company_id` | string | Yes      | Customer ID from `GET /customers`.             |
| `query`      | string | Yes      | The user's question or message.                |

```
GET /chat?company_id=proficio&query=Tell+me+about+this+company
```

**Response**

`200 OK` — `Content-Type: text/plain`, streamed body.

The response body arrives incrementally as the model generates tokens. There is no JSON envelope — the raw text is the answer. The stream ends when the model finishes.

**Reading the stream**

```js
const res = await fetch(
  `/chat?company_id=${encodeURIComponent(companyId)}&query=${encodeURIComponent(query)}`
);

const reader = res.body.getReader();
const decoder = new TextDecoder();
let fullText = '';

while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value, { stream: true });
  fullText += chunk;
  // Update UI incrementally here
}
```

**Context / session behaviour**

- The backend maintains a per-process conversation history.
- Switching `company_id` resets the conversation history automatically.
- There is no explicit session token — history is global to the server process. For multi-user deployments this must be addressed server-side.

---

## Error handling

The API currently returns FastAPI's default error responses.

| Scenario                    | Status | Body                                      |
|-----------------------------|--------|-------------------------------------------|
| Missing required query param | `422`  | `{ "detail": [...] }` (Unprocessable Entity) |
| Unknown `company_id`         | `500`  | Server error — no customer directory found |

Always check `res.ok` before reading the body. For streaming, also handle network errors on `reader.read()`.

```js
if (!res.ok) {
  const err = await res.json().catch(() => ({}));
  console.error('API error', res.status, err);
  return;
}
```

---

## Typical integration flow

```
1. App loads
       └─ GET /customers
              └─ render customer picker

2. User selects a customer + types a query
       └─ GET /chat?company_id=<id>&query=<text>
              └─ open ReadableStream
              └─ append chunks to UI as they arrive
              └─ stream ends → response complete
```

---

## Running locally

```bash
uvicorn main:app --reload
```

The server starts on `http://localhost:8000`. The interactive Swagger UI is available at `http://localhost:8000/docs`.
