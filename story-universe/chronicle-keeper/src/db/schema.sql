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

CREATE TABLE IF NOT EXISTS factions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    ideology TEXT,
    relationships TEXT
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

-- System-level key/value for global runtime values (e.g., world time)
CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value TEXT
);
