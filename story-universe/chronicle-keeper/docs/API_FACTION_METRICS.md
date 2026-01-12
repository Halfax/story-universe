**Faction Metrics API**

- **GET /world/factions/{id}/metrics**: returns JSON `{faction_id, trust, power, resources, influence}`. Defaults used when metrics row missing.
- **PUT /world/factions/{id}/metrics**: partial update/upsert. Accepts JSON with any of `{trust, power, resources, influence}`. Requires admin API key.

Seed script
- `scripts/seed_faction_metrics.py` — reads CSV with columns `name,trust,power,resources,influence` and applies upserts to `faction_metrics`.
  - Dry-run by default; use `--commit` to apply changes.
  - Use `--create` to create missing factions when a name isn't found.

Example: dry-run
```sh
python scripts/seed_faction_metrics.py --csv data/faction_metrics.csv
```

Example: commit and create missing factions
```sh
python scripts/seed_faction_metrics.py --csv data/faction_metrics.csv --create --commit
```

API example (update trust)
```sh
curl -X PUT "http://localhost:8000/world/factions/42/metrics" -H "X-API-KEY: <ADMIN_KEY>" -H "Content-Type: application/json" -d '{"trust": 0.75}'
```
