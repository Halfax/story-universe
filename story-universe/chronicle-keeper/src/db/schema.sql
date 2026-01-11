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

-- Add more tables as needed (factions, events, etc.)
