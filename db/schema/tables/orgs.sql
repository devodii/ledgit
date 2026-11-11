CREATE TABLE orgs (
    slug TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT NOT NULL DEFAULT '',
    country TEXT NOT NULL DEFAULT ''
);
