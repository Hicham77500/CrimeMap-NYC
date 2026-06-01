# CrimeMap NYC

Plateforme de visualisation et d'analyse de la criminalité à New York à partir des données Open Data du NYPD.

## Objectifs

- Analyse spatio-temporelle
- Corrélation crime / zone géographique
- Prévision de criminalité
- Application web interactive

## Membres de l'équipe

- Développeur Domaine
- Dev 1 Data & IA
- Dev 2 Backend
- Dev 3 Frontend

## Technologies

### Frontend

- React
- TypeScript
- Leaflet
- Recharts

### Backend

- FastAPI
- SQLAlchemy

### Base de données

- PostgreSQL
- PostGIS

### Data Science

- Pandas
- Scikit-Learn
- DBSCAN

## Structure du projet

```text
frontend/
backend/
database/
data/
notebooks/
ml/
docs/
PROJECT_GUIDE.md
```

## Dataset

Source : NYC Open Data

Dataset principal : NYPD Complaint Data Historic

## Fonctionnalités

### Carte

- Affichage des crimes
- Zoom
- Heatmap
- Clustering

### Filtres

- Année
- Mois
- Borough
- Type de crime

### Dashboard

- Nombre total de crimes
- Crimes par borough
- Crimes par heure
- Crimes par catégorie

### IA

- Prévision du nombre de crimes
- Détection de zones à risque

## API

- GET /crimes
- GET /crimes/search
- GET /stats
- GET /heatmap
- GET /prediction

## Contrat de données

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
