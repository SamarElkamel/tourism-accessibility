# Tourism Accessibility – Paris Open Data (End-to-End ETL + Dataviz)

Projet DevOps/Data: ingestion d’open-data de la Ville de Paris, stockage MySQL, traitement ETL et visualisation web statique.

- Source open-data: https://opendata.paris.fr/pages/home/
- Sujet choisi: Accessibilité des hébergements en Île-de-France
- SGBD: MySQL 8.0
- Front: page statique avec Chart.js (servie via `python -m http.server`)
- Orchestration: Docker + Docker Compose
- Tests: smoke test (pytest)

## Architecture

```
.
├─ docker/
│  ├─ docker-compose.yml      # db (MySQL), etl (job), app (static server)
│  ├─ init.sql                # création DB, table, et utilisateur applicatif
│  └─ requirements.txt        # dépendances Python (pinnées)
├─ etl/
│  ├─ load_data_mysql.py      # (E+L) récupère via API et insère en MySQL
│  └─ prepare_for_viz.py      # (T) agrégations + export JSON pour la dataviz
├─ dataviz/
│  ├─ index.html              # page Chart.js
│  └─ data_for_viz.json       # généré par l’ETL (sortie)
├─ scripts/
│  └─ run_etl.sh              # lance les 2 étapes ETL
├─ tests/
│  └─ test_smoke.py           # test basique
├─ Dockerfile                 # image unique pour ETL + app
└─ README.md
```

## Fonctionnalités

- Ingestion par API (Ville de Paris).
- Stockage en MySQL 8.0 avec table `hebergements`.
- Transformations/agrégations:
  - Proportion globale d’hébergements accessibles.
  - Répartition par code postal (totaux + % accessibles).
  - Top 5 communes par accessibilité.
  - Liste des communes < 50% d’accessibilité.
- Export JSON: `dataviz/data_for_viz.json`.
- Dataviz: 3 graphiques (doughnut global, barres par code postal, barres top communes).

## Démarrage rapide

Prérequis: Docker et Docker Compose.

1. Construire et lancer:
   ```
   docker compose -f docker/docker-compose.yml up --build
   ```
   - `db`: démarre MySQL et initialise la base/table.
   - `etl`: attend la santé de la DB puis exécute le job `scripts/run_etl.sh` (insère les données et génère `dataviz/data_for_viz.json`).
   - `app`: sert la dataviz sur http://localhost:8000

2. Ouvrir la dataviz:
   - Pour éviter les erreurs CORS, lancez un serveur local Python puis ouvrez l'URL suivante:
     - Windows: `python -m http.server 8000 --directory dataviz`
     - Linux/macOS: `python3 -m http.server 8000 --directory dataviz`
     - Ensuite ouvrez: http://127.0.0.1:8000

3. Arrêt:
   ```
   docker compose -f docker/docker-compose.yml down
   ```
   Le volume de données `db_data` persiste entre les runs.

## Variables d’environnement

Les services utilisent des variables standard 12-factor (voir `docker/docker-compose.yml`):

- `MYSQL_HOST` (par défaut `db`)
- `MYSQL_DATABASE` (par défaut `tourismdb`)
- `MYSQL_USER` (par défaut `root`)
- `MYSQL_PASSWORD` (par défaut vide pour ce test)
- `PORT` (pour le serveur statique, par défaut `8000`)


## Tests

Exécuter les tests dans le conteneur ETL:

```
docker compose -f docker/docker-compose.yml run --rm etl pytest -q
```

Sortie attendue: test de fumée OK.

## Détails techniques

- Extraction (`etl/load_data_mysql.py`):
  - Endpoint Paris OpenData: `accessibilite-des-hebergements-en-ile-de-france-paris-je-t-aime` (limit=100).
  - Champs extraits (exemples): `etablissement`, `adresse`, `ville`, `code_postal`, `latitude`, `longitude`.
  - Dérivation `accessibilite` (Oui/Non) selon présence d’attribut d’accessibilité dans l’enregistrement source.
- Transformation et export (`etl/prepare_for_viz.py`):
  - Calculs d’agrégats (global, par code postal, par commune).
  - Export JSON lisible par la page Chart.js.

## 12-Factor & Bonnes pratiques DevOps

- Config par variables d’environnement: OK (MYSQL_*, PORT).
- Dépendances explicites et pinnées: OK (`docker/requirements.txt`).
- Logs sur stdout: OK (scripts ETL).
- Processus stateless; persistance externalisée: OK (volume `db_data`).
- Port binding: OK (app écoute sur 8000).
- Dev/prod parity: bonne via Compose.
- Admin tasks: ETL est un one-off job (commande dédiée).
- Build/Release/Run: simplifié en une image commune pour ETL et app (trade-off volontaire pour ce test).
- Sécurité (note): mot de passe root vide pour simplifier le run local; en production, utiliser des secrets et un compte applicatif non-root.


## Maintenance & Évolutions

- Surveiller les changements de schéma de l’API.
- Améliorer l’observabilité (metrics + logs centralisés).
- Étendre la couverture de tests (intégration MySQL, validité du JSON exporté).
- Séparer images (job ETL vs serveur) et utiliser un compte MySQL applicatif par défaut.

## Licence

Usage libre pour évaluation technique.
