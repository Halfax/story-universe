**API: Bulk import factions**

Endpoint
- `POST /world/factions/import`

Authentication
- Requires admin API key header `X-API-Key: <ADMIN_KEY>` (same as other admin endpoints).

Payload
- JSON body with fields:
  - `names`: array of faction name strings (required)
  - `skip_existing`: boolean (default true) — skip names already present in DB

Example (single request)
```bash
curl -X POST http://PI_HOST:8001/world/factions/import \
  -H "X-API-Key: $ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"names":["House Dawn","Order of the Wyr"],"skip_existing":true}'
```

Batching guidance
- For large datasets (thousands of names) POST in chunks (e.g., 500 names per request).
- Use `skip_existing=true` to make the import idempotent and safe for retries.

Recommended client workflow
1. Read CSV and split into chunks of 250–1000 names.
2. For each chunk, `POST /world/factions/import` with `skip_existing=true`.
3. Track responses and retry failed chunks.

Server behavior
- The endpoint inserts any non-existing names into the `factions` table with default metadata and returns `{'status':'imported','inserted': N}`.

Permissions & safety
- Only admin keys may access this endpoint. If running in production, restrict access to internal networks and monitor logs.
