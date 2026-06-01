# Data & IA - Source de données

## Source retenue

- Site : NYC Open Data
- Dataset : NYC crime
- Page source : https://data.cityofnewyork.us/Public-Safety/NYC-crime/qb7u-rbmr/about_data

## Ce que le dataset fournit

- 24 colonnes
- Crimes reportés à la NYPD
- Couverture des délits felony, misdemeanor et violation
- Mise à jour trimestrielle
- Dernière mise à jour des données : 28 avril 2026

## Champs utiles pour la suite

- BORO_NM : borough
- CMPLNT_FR_DT : date
- CMPLNT_FR_TM : heure
- OFNS_DESC : catégorie de crime
- LAW_CAT_CD : niveau d’infraction
- Latitude / Longitude si disponibles dans le jeu de données

## Première direction analytique

- Nettoyage des dates et heures
- Normalisation des boroughs
- Agrégation spatio-temporelle
- Préparation d’indicateurs pour prévision et détection de zones à risque

## Remarque

Le dataset public est une vue communautaire basée sur les données NYPD Complaint Data Current (Year To Date).