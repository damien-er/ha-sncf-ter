# Changelog
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) ; versionnage [SemVer](https://semver.org/lang/fr/).

## [2.0.0] – 2026-10-08
### Ajouté
- Premier dépôt public : package renommé `sncf_basse_indre.yaml`, README, licence MIT, tests pytest et CI GitHub Actions.
- `examples/secrets.example.yaml` et `examples/sample_departures.json`.
### Modifié
- Historique antérieur repris du journal du package ci-dessous (v1.x).

## [1.2.0] – 2026-07-10
### Ajouté
- Sens Nantes : capteurs `sncf_train_bi_nantes_1/2/3` filtrant sur « Nantes » (`selectattr`), en parallèle des capteurs Savenay désormais filtrés par `rejectattr`. Aucune requête API supplémentaire.

## [1.1.0] – 2026-07-10
### Corrigé
- Authentification : `authentication: basic` + `username: !secret` n'envoyait pas le jeton (réponse « no token »). Remplacé par un en-tête `Authorization` pré-encodé en base64 (`sncf_api_token_b64`). Vérifié sur un capteur de test.
### Nettoyé
- Suppression d'un bloc commenté obsolète et du capteur de test temporaire.
### Limite connue
- Si le jeton est régénéré, recalculer le secret.

## [1.0.0] – 2026-07-06
### Ajouté
- 4 capteurs pour Basse-Indre (brut + 3 trains) via l'API SNCF / Navitia.
