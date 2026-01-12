-- Chronicle Keeper DB Schema (initial)
CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    traits TEXT,
    location_id INTEGER,
    status TEXT
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- Factions table (enhanced). If an older simple `factions` table exists,
-- it will remain untouched; operators can migrate rows manually if desired.
CREATE TABLE IF NOT EXISTS factions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    ideology TEXT,
    relationships TEXT,
    power INTEGER DEFAULT 0,
    resources INTEGER DEFAULT 0,
    trust REAL DEFAULT 0.5,
    influence INTEGER DEFAULT 0,
    personality_traits TEXT,
    metadata TEXT
);

-- enhanced location metadata
ALTER TABLE locations RENAME TO locations_old;
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    region TEXT,
    forbidden INTEGER DEFAULT 0,
    locked INTEGER DEFAULT 0,
    political_status TEXT,
    metadata TEXT
);
-- migrate existing rows if any
INSERT OR IGNORE INTO locations (id, name) SELECT id, name FROM locations_old;
DROP TABLE IF EXISTS locations_old;

-- Items and inventory
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    sub_type TEXT,
    weight REAL DEFAULT 0,
    stackable INTEGER DEFAULT 0,
    max_stack INTEGER DEFAULT 1,
    equippable INTEGER DEFAULT 0,
    equip_slot TEXT,
    damage_min INTEGER,
    damage_max INTEGER,
    armor_rating INTEGER,
    durability_max INTEGER,
    consumable INTEGER DEFAULT 0,
    charges_max INTEGER,
    effects TEXT,
    tags TEXT
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_type TEXT NOT NULL, -- 'character' or 'container'
    owner_id TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    durability INTEGER,
    charges_remaining INTEGER,
    equipped INTEGER DEFAULT 0,
    equip_slot TEXT,
    metadata TEXT,
    FOREIGN KEY(item_id) REFERENCES items(id)
);

-- Add more tables as needed (factions, events, etc.)

-- Per-character structured runtime state (preferred over world_state JSON blobs)
CREATE TABLE IF NOT EXISTS character_state (
    character_id INTEGER PRIMARY KEY,
    state TEXT,
    last_updated INTEGER,
    FOREIGN KEY(character_id) REFERENCES characters(id)
);

-- Faction membership and runtime state
CREATE TABLE IF NOT EXISTS faction_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faction_id INTEGER NOT NULL,
    character_id INTEGER NOT NULL,
    role TEXT,
    joined_at INTEGER,
    FOREIGN KEY(faction_id) REFERENCES factions(id),
    FOREIGN KEY(character_id) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS faction_state (
    faction_id INTEGER PRIMARY KEY,
    state TEXT,
    last_updated INTEGER,
    FOREIGN KEY(faction_id) REFERENCES factions(id)
);

CREATE TABLE IF NOT EXISTS faction_metrics (
    faction_id INTEGER PRIMARY KEY,
    trust REAL DEFAULT 0.5,
    power INTEGER DEFAULT 0,
    resources INTEGER DEFAULT 0,
    influence INTEGER DEFAULT 0,
    FOREIGN KEY(faction_id) REFERENCES factions(id)
);

-- Canonical directed relationships between factions. Stores explicit typed relations and numeric strength.
CREATE TABLE IF NOT EXISTS faction_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_faction_id INTEGER NOT NULL,
    target_faction_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL, -- e.g., ally, neutral, rival, enemy, vassal, trade_partner
    strength REAL DEFAULT 0.0, -- [-1.0 .. 1.0] where negative indicates hostility, positive indicates friendliness
    last_updated INTEGER,
    cooldown_until INTEGER DEFAULT 0, -- epoch ts until which actions are restricted
    metadata TEXT,
    FOREIGN KEY(source_faction_id) REFERENCES factions(id),
    FOREIGN KEY(target_faction_id) REFERENCES factions(id)
);

-- Per-faction cooldowns for non-relationship actions (keyed by name)
CREATE TABLE IF NOT EXISTS faction_cooldowns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faction_id INTEGER NOT NULL,
    cooldown_key TEXT NOT NULL,
    until_ts INTEGER NOT NULL,
    metadata TEXT,
    FOREIGN KEY(faction_id) REFERENCES factions(id)
);

-- System-level key/value for global runtime values (e.g., world time)
CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value TEXT
);
