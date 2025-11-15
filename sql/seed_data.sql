-- Seed data for reference tables
-- Idempotent inserts using INSERT OR IGNORE
-- Applied after schema initialization

-- Account types
INSERT OR IGNORE INTO account_types (label, description) VALUES
    ('Checking', 'Personal or business checking account'),
    ('Savings', 'Savings account'),
    ('Credit Card', 'Credit card account'),
    ('Cash', 'Physical cash');

-- Payment types
INSERT OR IGNORE INTO payment_types (name, description) VALUES
    ('Cash', 'Physical cash payment'),
    ('Debit', 'Debit card payment'),
    ('Credit Card', 'Credit card payment'),
    ('E-Transfer', 'Electronic transfer (Interac, etc.)');

-- Timeline sources
INSERT OR IGNORE INTO timeline_sources (name, description) VALUES
    ('rescuetime', 'RescueTime time tracking data'),
    ('screentime', 'macOS/iOS ScreenTime data'),
    ('geofency', 'Geofency location tracking data');

