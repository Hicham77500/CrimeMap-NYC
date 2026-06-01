# CrimeMap NYC — Guide du projet

Plateforme de visualisation et d'analyse de la criminalité à New York, basée sur les données Open Data du NYPD.

---

## Objectifs

- Analyse spatio-temporelle des crimes déclarés à la NYPD
- Corrélation crime / zone géographique (borough, heure, catégorie)
- Détection automatique des hotspots criminels (DBSCAN)
- Application web interactive avec carte, heatmap et dashboard

---

## Équipe — 2 développeurs

### Développeur 1 — Data & IA (≈ 50 %)

**Mission :** Gestion des données Open Data, nettoyage, analyse statistique, détection des hotspots, préparation pour la base.

**Tâches :**
- Récupération des datasets NYPD (NYC Open Data)
- Nettoyage et normalisation des données
- Scripts ETL (`ml/`)
- Analyse exploratoire (`notebooks/`)
- Modèle DBSCAN (hotspots)
- Génération des statistiques dashboard
- Documentation des données

**Livrables :**
- Dataset nettoyé (`data/processed/nyc_crime_clean.csv`)
- Scripts d'import (`database/import_crimes.sql`)
- Analyses statistiques (`data/processed/stats/`)
- Modèle de clustering (hotspots DBSCAN)
- Documentation Data

---

### Développeur 2 — Full Stack (≈ 50 %)

**Mission :** Développement complet de la plateforme web (backend + frontend).

**Backend :**
- Base de données PostgreSQL + PostGIS
- API REST FastAPI + SQLAlchemy

**Frontend :**
- React + TypeScript
- Carte interactive Leaflet
- Dashboard Recharts
- Intégration API

**Tâches :**
- Architecture du projet
- Schéma et migrations base de données
- Endpoints REST (`/crimes`, `/stats`, `/heatmap`, `/prediction`)
- Carte interactive avec clustering et heatmap
- Dashboard filtrable (borough, mois, type de crime)
- Barre de recherche

**Livrables :**
- Base PostgreSQL opérationnelle
- API FastAPI documentée
- Frontend React déployable
- Carte interactive
- Dashboard final

---

## Flux de travail

```
NYC Open Data (API)
       │
       ▼
ml/nyc_crime_pipeline.py   ← ETL, nettoyage, DBSCAN
       │
       ▼
data/processed/            ← CSV nettoyés + hotspots + stats
       │
       ▼
database/ (PostgreSQL)     ← schema.sql + import_crimes.sql
       │
       ▼
backend/ (FastAPI)         ← API REST
       │
       ▼
frontend/ (React)          ← Carte + Dashboard
```

---

## Technologies

| Couche | Stack |
|---|---|
| Data | Python, Pandas, Scikit-Learn (DBSCAN), Matplotlib |
| Base de données | PostgreSQL, PostGIS |
| Backend | FastAPI, SQLAlchemy |
| Frontend | React, TypeScript, Leaflet, Recharts |

---

## Structure du projet

```text
CrimeMap-NYC/
├── ml/                        # Pipeline ETL + modèles IA
│   ├── nyc_crime_pipeline.py  # ETL, nettoyage, stats, DBSCAN
│   ├── run_pipeline.py        # Entrypoint CLI
│   └── requirements.txt
├── notebooks/
│   └── 01_exploration_crime_data.ipynb  # EDA complet
├── database/
│   ├── schema.sql             # Tables crimes + hotspots (PostGIS)
│   └── import_crimes.sql      # Import CSV → PostgreSQL
├── backend/                   # FastAPI (à développer)
├── frontend/                  # React + TypeScript (à développer)
├── data/                      # Ignoré par Git (trop lourd)
│   ├── raw/
│   └── processed/
│       ├── nyc_crime_clean.csv
│       ├── nyc_crime_hotspots.csv
│       └── stats/
├── docs/
│   ├── api.md
│   ├── data-contract.md
│   └── data-sourcing.md
├── .gitignore
├── PROJECT_GUIDE.md
└── README.md
```

---

## Datasets

| Dataset | Lignes | Période | ID NYC Open Data |
|---|---|---|---|
| NYPD Complaint Data Current (YTD) | ~133K | 2025 | `5uac-w243` |
| NYPD Complaint Data Historic | ~10M | 2006–2025 | `qgea-i56i` |

Le pipeline utilise l'API YTD par défaut. Passer `DATASET_URL_HISTORIC` pour l'analyse complète.

---

## API — Endpoints prévus

| Méthode | Route | Description |
|---|---|---|
| GET | `/crimes` | Liste paginée des crimes |
| GET | `/crimes/search` | Recherche par critères |
| GET | `/stats` | Agrégations dashboard |
| GET | `/heatmap` | Points pour la heatmap Leaflet |
| GET | `/prediction` | Prévisions IA |

---

## Contrat de données canonique

```json
{
  "id": 1,
  "date": "YYYY-MM-DD",
  "borough": "string",
  "crime_type": "string",
  "latitude": 40.7128,
  "longitude": -74.006
}
```

## Workflow Git

- main
- develop
- feature/data
- feature/backend
- feature/frontend

## Règles

- Pas de push direct sur main
- Pull Request obligatoire
- Documentation mise à jour à chaque fonctionnalité
- Toute modification API doit être documentée

## Définition de terminé

- Fonctionnalité testée
- Code poussé
- Documentation mise à jour
- Validation par les autres membres
