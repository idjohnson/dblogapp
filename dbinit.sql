-- Connect to your 'myhost' database first
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ DEFAULT NOW(),
    log_level VARCHAR(50),
    message TEXT
);

INSERT INTO logs (log_level, message) VALUES
('INFO', 'Application started successfully.'),
('WARNING', 'Low disk space detected on /var/log.'),
('ERROR', 'Failed to connect to external payment gateway.'),
('INFO', 'User admin logged in.');
