CREATE TABLE IF NOT EXISTS events(
    'ID' VARCHAR(255) PRIMARY KEY, 
    'Artist' VARCHAR(255), 
    'City' VARCHAR(255), 
    'Vanue' VARCHAR(255), 
    'Date' DATETIME UNIQUE
);
CREATE TABLE IF NOT EXISTS cookies(
    'ID' INTEGER,
    'Name' VARCHAR(255), 
    'Value' TEXT, 
    'Domain' VARCHAR(255), 
    'Expires' DATETIME, 
    'CreatedOn' DATETIME,
    PRIMARY KEY('ID' AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS cookies_per_log(
    'ID' INTEGER,
    'LogId' INTEGER, 
    'CookieId' INTEGER, 
    'CreatedOn' DATETIME,
    PRIMARY KEY('ID' AUTOINCREMENT),
    FOREIGN KEY (LogId) REFERENCES logs (ID),
    FOREIGN KEY (CookieId) REFERENCES cookies (ID)
);
CREATE TABLE IF NOT EXISTS logs(
    'ID' INTEGER,
    'EventId' VARCHAR(255), 
    'Status' INTEGER, 
    'Quantity' INTEGER, 
    'Total' INTEGER, 
    'Picks' TEXT, 
    'Descriptions' TEXT, 
    'CreatedOn' DATETIME,
    PRIMARY KEY('ID' AUTOINCREMENT),
    FOREIGN KEY (EventId) REFERENCES events (ID)
);
CREATE TABLE IF NOT EXISTS picks(
    'ID' INTEGER,
    'EventId' VARCHAR(255), 
    'Picks' TEXT, 
    'CreatedOn' DATETIME,
    PRIMARY KEY('ID' AUTOINCREMENT),
    FOREIGN KEY (EventId) REFERENCES events (ID)
);
INSERT OR REPLACE INTO events (ID, Artist, City, Vanue, Date) VALUES('23006130DAB40C0B', 'Coldplay', 'London', 'Wembley Stadium', '2025-08-22');
INSERT OR REPLACE INTO events (ID, Artist, City, Vanue, Date) VALUES('23006130DBA60C0D', 'Coldplay', 'London', 'Wembley Stadium', '2025-08-23');
INSERT OR REPLACE INTO events (ID, Artist, City, Vanue, Date) VALUES('23006130DCBE0C15', 'Coldplay', 'London', 'Wembley Stadium', '2025-08-26');
INSERT OR REPLACE INTO events (ID, Artist, City, Vanue, Date) VALUES('23006130DD430C17', 'Coldplay', 'London', 'Wembley Stadium', '2025-08-27');