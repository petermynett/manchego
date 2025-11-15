-- Baseline schema for manchego database
-- This schema is updated after each migration to reflect current state

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Migration tracking table
CREATE TABLE IF NOT EXISTS migrations (
    filename TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

-- Account types reference table
CREATE TABLE IF NOT EXISTS account_types (
    label TEXT PRIMARY KEY,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Payment types reference table
CREATE TABLE IF NOT EXISTS payment_types (
    name TEXT PRIMARY KEY,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Timeline sources reference table
CREATE TABLE IF NOT EXISTS timeline_sources (
    name TEXT PRIMARY KEY,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

