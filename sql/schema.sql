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

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id                  TEXT PRIMARY KEY,
    account_type_label  TEXT NOT NULL REFERENCES account_types(label),
    institution         TEXT,
    account_name        TEXT,
    account_number      TEXT,
    is_active           BOOLEAN DEFAULT TRUE,
    initial_balance     REAL DEFAULT 0.0,
    currency            TEXT DEFAULT 'CAD',
    notes               TEXT,
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_accounts_account_type_label ON accounts(account_type_label);
CREATE INDEX idx_accounts_is_active ON accounts(is_active);

-- Ledger table
CREATE TABLE IF NOT EXISTS ledger (
    id                  TEXT PRIMARY KEY,
    transaction_date    TEXT NOT NULL,
    transaction_time    TEXT,
    description         TEXT NOT NULL,
    amount              REAL NOT NULL,
    currency            TEXT DEFAULT 'CAD',
    account_id          TEXT NOT NULL REFERENCES accounts(id),
    vendor_id           TEXT REFERENCES vendors(id),
    location_id         TEXT REFERENCES locations(id),
    category            TEXT,
    source_filename     TEXT,
    internal_note       TEXT,
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_ledger_account_id ON ledger(account_id);
CREATE INDEX idx_ledger_transaction_date ON ledger(transaction_date);
CREATE INDEX idx_ledger_vendor_id ON ledger(vendor_id);
CREATE INDEX idx_ledger_location_id ON ledger(location_id);

