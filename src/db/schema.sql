-- Minimal DB schema for tests

CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    traits TEXT,
    location_id INTEGER,
    status TEXT,
    faction_id INTEGER,
    attrs TEXT
);

CREATE TABLE IF NOT EXISTS factions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ideology TEXT,
    relationships TEXT,
    personality_traits TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    properties TEXT
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER,
    item_id INTEGER,
    quantity INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS faction_relationships (
    source_faction_id INTEGER,
    target_faction_id INTEGER,
    relationship_type TEXT,
    strength REAL,
    cooldown_until INTEGER
);

CREATE TABLE IF NOT EXISTS faction_metrics (
    faction_id INTEGER PRIMARY KEY,
    trust REAL DEFAULT 0.0,
    power REAL DEFAULT 0.0,
    resources REAL DEFAULT 0.0,
    influence REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS faction_cooldowns (
    faction_id INTEGER,
    cooldown_key TEXT,
    until_ts INTEGER
);

CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER,
    type TEXT,
    description TEXT,
    involved_characters TEXT,
    involved_locations TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS event_consequences (
    event_id TEXT PRIMARY KEY,
    reversible INTEGER DEFAULT 0,
    undo_payload TEXT,
    applied_ts INTEGER,
    metadata TEXT
);
