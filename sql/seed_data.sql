-- Seed data for reference tables
-- Idempotent inserts using INSERT OR IGNORE
-- Applied after schema initialization

-- ────────────────────────────────────────────────────────────────────────
-- ACCOUNT TYPES
-- ────────────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO account_types (label, description) VALUES
    ('Checking', 'Day-to-day transaction account'),
    ('Savings', 'Interest-bearing savings account'),
    ('Credit Card', 'Revolving credit account'),
    ('Cash', 'Physical cash on hand'),
    ('Digital Wallet', 'PayPal, Venmo, etc.'),
    ('Transit Card', 'Prepaid transit passes'),
    ('Investment', 'Brokerage or retirement accounts');

-- ────────────────────────────────────────────────────────────────────────
-- PAYMENT TYPES
-- ────────────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO payment_types (name, description) VALUES
    ('Cash', 'Physical cash payment'),
    ('Debit Card', 'Direct bank account debit'),
    ('Credit Card', 'Credit card payment'),
    ('E-Transfer', 'Electronic money transfer'),
    ('Digital Wallet', 'PayPal, Apple Pay, etc.');

-- ────────────────────────────────────────────────────────────────────────
-- TIMELINE SOURCES
-- ────────────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO timeline_sources (name, description) VALUES
    ('rescuetime', 'RescueTime productivity tracking'),
    ('screentime', 'macOS Screen Time usage data'),
    ('geofency', 'Geofency location tracking'),
    ('google_calendar', 'Google Calendar events (future)'),
    ('google_maps', 'Google Maps timeline (future)');

-- ────────────────────────────────────────────────────────────────────────
-- VENDOR CATEGORIES
-- ────────────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO vendor_categories (label, description) VALUES
    ('F&B', 'Food and beverage establishments'),
    ('Software', 'Software and digital services'),
    ('Multi', 'Multi-category retailers'),
    ('Transport', 'Transportation services'),
    ('Banking', 'Financial institutions'),
    ('Clothing', 'Apparel and fashion'),
    ('Home', 'Home goods and services'),
    ('Music', 'Music and entertainment'),
    ('Core', 'Core/essential services'),
    ('Convenience', 'Convenience stores'),
    ('Electronics', 'Electronics and technology'),
    ('Services', 'Professional services'),
    ('Outdoor', 'Outdoor and sporting goods'),
    ('Cannabis', 'Cannabis products'),
    ('Groceries', 'Grocery stores');

-- ────────────────────────────────────────────────────────────────────────
-- ACCOUNTS
-- ────────────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO accounts (id, account_type_label, institution, account_name, account_number, is_active, currency) VALUES
    ('account-checking-uuid', 'Checking', 'CIBC', 'Personal Chequing', NULL, TRUE, 'CAD'),
    ('account-savings-uuid', 'Savings', 'CIBC', 'Business Savings', NULL, TRUE, 'CAD'),
    ('account-personal-visa-uuid', 'Credit Card', 'CIBC', 'Personal Visa', '9256', TRUE, 'CAD'),
    ('account-business-visa-uuid', 'Credit Card', 'CIBC', 'Business Visa', '4128', TRUE, 'CAD'),
    ('account-cash-uuid', 'Cash', 'CIBC', 'Cash', NULL, TRUE, 'CAD');
