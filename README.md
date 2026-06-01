# CrimeMap NYC

Plateforme de visualisation et d'analyse de la criminalité à New York, construite sur les données Open Data du NYPD.

---

## Aperçu

CrimeMap NYC permet d'explorer, de filtrer et d'analyser les crimes déclarés à la police de New York. Il combine une API REST, une base de données géospatiale et une interface web interactive pour cartographier les incidents, identifier les zones à risque et visualiser les tendances.

---

## Stack technique

| Couche | Technologies |
|---|---|
| **Data & IA** | Python · Pandas · Scikit-Learn · DBSCAN · Matplotlib |
| **Base de données** | PostgreSQL · PostGIS |
| **Backend** | FastAPI · SQLAlchemy |
| **Frontend** | React · TypeScript · Leaflet · Recharts |

---

## Fonctionnalités

- **Carte interactive** — affichage des crimes, zoom, heatmap, clustering visuel
- **Filtres** — par année, mois, borough, type de crime
- **Dashboard** — crimes totaux, par borough, par heure, par catégorie
- **Hotspots IA** — détection automatique des zones à risque via DBSCAN
- **API REST** — endpoints documentés pour consommer les données

---

## Démarrage rapide

### 1. Cloner le dépôt

```bash
git clone git@github.com:Hicham77500/CrimeMap-NYC.git
cd CrimeMap-NYC
```

### 2. Installer les dépendances data

```bash
pip install -r ml/requirements.txt
```

### 3. Lancer le pipeline ETL

```bash
cd ml
python run_pipeline.py
```

Cela :
- Télécharge les données depuis l'API NYC Open Data (YTD, ~133K lignes)
- Nettoie et normalise le dataset
- Génère les statistiques dashboard
- Calcule les hotspots DBSCAN

Les CSV produits atterrissent dans `data/processed/` (ignoré par Git).

### 4. Initialiser la base PostgreSQL

```bash
psql -d crimemap -U postgres -f database/schema.sql
psql -d crimemap -U postgres -f database/import_crimes.sql
```

### 5. Démarrer le backend

```bash
cd backend
uvicorn main:app --reload
```

### 6. Démarrer le frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Structure du projet

```text
CrimeMap-NYC/
├── ml/                        # Pipeline ETL + modèles IA
│   ├── nyc_crime_pipeline.py  # Nettoyage, stats, DBSCAN
│   ├── run_pipeline.py        # Entrypoint CLI
│   └── requirements.txt
├── notebooks/
│   └── 01_exploration_crime_data.ipynb  # EDA complet
├── database/
│   ├── schema.sql             # Tables crimes + hotspots (PostGIS)
│   └── import_crimes.sql      # Import CSV → PostgreSQL
├── backend/                   # API FastAPI
├── frontend/                  # Application React
├── data/                      # Ignoré par Git
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

## Sources de données

| Dataset | Lignes | Période | Lien |
|---|---|---|---|
| NYPD Complaint Data Current (YTD) | ~133K | 2025 | [NYC Open Data 5uac-w243](https://data.cityofnewyork.us/Public-Safety/NYPD-Complaint-Data-Current-Year-To-Date-/5uac-w243) |
| NYPD Complaint Data Historic | ~10M | 2006–2025 | [NYC Open Data qgea-i56i](https://data.cityofnewyork.us/Public-Safety/NYPD-Complaint-Data-Historic/qgea-i56i) |

---

## API — Endpoints

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/crimes` | Liste paginée des crimes |
| `GET` | `/crimes/search` | Recherche par critères |
| `GET` | `/stats` | Agrégations pour le dashboard |
| `GET` | `/heatmap` | Points géolocalisés pour la heatmap |
| `GET` | `/prediction` | Prévisions IA |

---

## Contrat de données

Chaque enregistrement exposé par l'API respecte ce schéma canonique :

```json
{
  "id": "string",
  "date": "YYYY-MM-DD",
  "borough": "string",
  "crime_type": "string",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

---

## Workflow Git

| Branche | Usage |
|---|---|
| `main` | Production — PR obligatoire |
| `develop` | Intégration |
| `feature/data` | Pipeline data & IA |
| `feature/backend` | API FastAPI |
| `feature/frontend` | Interface React |

---

## Documentation

- [data-sourcing.md](docs/data-sourcing.md) — sources et champs NYPD
- [data-contract.md](docs/data-contract.md) — schéma canonique
- [api.md](docs/api.md) — contrats API
- [PROJECT_GUIDE.md](PROJECT_GUIDE.md) — guide complet (équipe, flux, architecture)
