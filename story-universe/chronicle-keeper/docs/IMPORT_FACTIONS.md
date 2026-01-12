**Importing faction names from CSV into Chronicle Keeper (Pi)**

Overview
- This guide explains how to promote names from `chronicle-keeper/data/faction_names.csv` into the Pi (Chronicle Keeper) database `factions` table. Use the import script for local DB imports or the API endpoint for remote/import-as-a-service.

Important: ALWAYS perform a dry-run first and ensure you have a backup of your DB.

Local script (dry-run by default)
- Script: `chronicle-keeper/scripts/import_factions.py`
- Dry-run (safe):
```powershell
python chronicle-keeper/scripts/import_factions.py --csv chronicle-keeper/data/faction_names.csv
```
- Commit (write to DB):
```powershell
python chronicle-keeper/scripts/import_factions.py --csv chronicle-keeper/data/faction_names.csv --commit
```
- What the script does:
  - Reads the CSV and counts unique names.
  - Finds existing names in the `factions` table and reports how many would be inserted.
  - With `--commit` it inserts new rows in batches and commits.

Backups & safety
- The script will not modify your DB without `--commit`.
- BEFORE running `--commit`, create a DB backup (simple copy of the SQLite file):
```powershell
copy %CHRONICLE_KEEPER_DB_PATH% %CHRONICLE_KEEPER_DB_PATH%.bak
```
- If your Pi uses a filesystem DB path inside the repo, back up `chronicle-keeper/universe.db`.

When the DB schema is missing
- If the `factions` table is absent, run the DB initializer or apply `chronicle-keeper/src/db/schema.sql` first. See `chronicle-keeper/src/db/init_db.py` for helpers.

Batching and scale
- For very large CSVs or remote systems prefer using the API endpoint in chunks (see `API_FACTIONS_IMPORT.md`).

Rollback
- If something goes wrong after commit, restore from the DB backup and re-run with curated inputs.

Notes
- The import script inserts minimal metadata (`ideology` set to NULL and `relationships` as an empty JSON string). After import, enrich records using Pi's `/world/factions/{id}` update API.
