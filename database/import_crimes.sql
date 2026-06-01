-- ============================================================
-- CrimeMap NYC — Import des données nettoyées en PostgreSQL
-- Usage :
--   psql -d crimemap -U postgres -f database/import_crimes.sql
--
-- Prérequis :
--   - Schema créé (database/schema.sql)
--   - Fichier data/processed/nyc_crime_clean.csv accessible
--     depuis le répertoire courant du serveur PostgreSQL
--     OU utiliser \copy (côté client) :
--     \copy crimes(id,date,borough,crime_type,latitude,longitude)
--       FROM 'data/processed/nyc_crime_clean.csv' CSV HEADER;
-- ============================================================

-- Vider les tables avant re-import (idempotent)
TRUNCATE TABLE hotspots;
TRUNCATE TABLE crimes;

-- Import crimes nettoyés
-- Adapter le chemin absolu si nécessaire
\copy crimes(id, date, borough, crime_type, latitude, longitude) \
    FROM 'data/processed/nyc_crime_clean.csv' \
    WITH (FORMAT csv, HEADER true, NULL '');

-- Import hotspots DBSCAN
\copy hotspots(cluster_id, latitude, longitude, crime_count) \
    FROM 'data/processed/nyc_crime_hotspots.csv' \
    WITH (FORMAT csv, HEADER true, NULL '');

-- Vérification rapide
SELECT 'crimes'   AS table_name, COUNT(*) AS rows FROM crimes
UNION ALL
SELECT 'hotspots' AS table_name, COUNT(*) AS rows FROM hotspots;
