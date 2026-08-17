-- schema.sql — Person B, Zone 3 (Hour 3:30-4:15 of the plan).
-- Run this via farm_memory.py's init function to create the SQLite DB.
-- Tables per the plan: farm, observations, diagnoses, advisories, livestock.

CREATE TABLE IF NOT EXISTS farm (
    farm_id     TEXT PRIMARY KEY,
    phone       TEXT UNIQUE,
    pin         TEXT,            -- DEMO ONLY: production must hash+salt
    farmer_name TEXT,
    location    TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS livestock (
    animal_id   TEXT PRIMARY KEY,
    farm_id     TEXT NOT NULL REFERENCES farm(farm_id),
    species     TEXT,
    tag_number  TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- One row per analysis run (crop photo, livestock photo, or voice-only check)
CREATE TABLE IF NOT EXISTS observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    farm_id         TEXT NOT NULL REFERENCES farm(farm_id),
    animal_id       TEXT REFERENCES livestock(animal_id),   -- NULL for crop observations
    domain          TEXT NOT NULL CHECK (domain IN ('crop','livestock')),
    image_prediction TEXT,
    visual_confidence REAL,
    farmer_text     TEXT,
    sensor_json     TEXT,           -- raw JSON of contract #4, if any
    route           TEXT CHECK (route IN ('local','cloud')),
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS diagnoses (
    diagnosis_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    observation_id  INTEGER NOT NULL REFERENCES observations(observation_id),
    condition       TEXT NOT NULL,
    certainty       TEXT,            -- 'possible' | 'confirmed' | 'insufficient_evidence'
    final_confidence REAL,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS advisories (
    advisory_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    diagnosis_id    INTEGER NOT NULL REFERENCES diagnoses(diagnosis_id),
    source          TEXT CHECK (source IN ('local_offline','cloud_gemini')),
    summary         TEXT,
    actions_json    TEXT,            -- JSON list of action strings
    warning         TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_observations_farm ON observations(farm_id);
CREATE INDEX IF NOT EXISTS idx_diagnoses_observation ON diagnoses(observation_id);
