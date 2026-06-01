-- ============================================================
-- CrimeMap NYC — Schéma PostgreSQL
-- Prérequis : extension PostGIS activée
-- ============================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- ------------------------------------------------------------
-- Table principale : crimes
-- Correspond au data contract (id, date, borough, crime_type,
-- latitude, longitude) + colonnes utiles pour le dashboard
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crimes (
    id            TEXT        PRIMARY KEY,
    date          DATE        NOT NULL,
    borough       VARCHAR(50) NOT NULL,
    crime_type    TEXT        NOT NULL,
    latitude      NUMERIC(9, 6) NOT NULL,
    longitude     NUMERIC(9, 6) NOT NULL,
    geom          GEOMETRY(Point, 4326) GENERATED ALWAYS AS (
                      ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
                  ) STORED
);

-- Index géospatial pour les requêtes heatmap / zone
CREATE INDEX IF NOT EXISTS idx_crimes_geom    ON crimes USING GIST(geom);
-- Index temporel pour les filtres par date / mois
CREATE INDEX IF NOT EXISTS idx_crimes_date    ON crimes(date);
-- Index borough pour les agrégations dashboard
CREATE INDEX IF NOT EXISTS idx_crimes_borough ON crimes(borough);
-- Index type de crime pour les filtres
CREATE INDEX IF NOT EXISTS idx_crimes_type    ON crimes(crime_type);

-- ------------------------------------------------------------
-- Table des hotspots DBSCAN (générés par le pipeline ML)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hotspots (
    cluster_id    INTEGER     PRIMARY KEY,
    latitude      NUMERIC(9, 6) NOT NULL,
    longitude     NUMERIC(9, 6) NOT NULL,
    crime_count   INTEGER     NOT NULL,
    geom          GEOMETRY(Point, 4326) GENERATED ALWAYS AS (
                      ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
                  ) STORED
);

CREATE INDEX IF NOT EXISTS idx_hotspots_geom ON hotspots USING GIST(geom);
