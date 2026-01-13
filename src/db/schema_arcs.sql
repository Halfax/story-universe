-- SQL schema for narrative story arcs
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS arcs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    participants TEXT DEFAULT '[]', -- JSON array of participant character ids
    events TEXT DEFAULT '[]',       -- JSON array of event objects
    goals TEXT DEFAULT '[]',        -- JSON array or object describing arc goals
    data TEXT DEFAULT '{}'          -- JSON serialized additional payload
);
