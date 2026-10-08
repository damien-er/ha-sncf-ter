# HA SNCF TER – Basse-Indre
![Home Assistant](https://img.shields.io/badge/home--assistant-package-blue.svg?style=for-the-badge&logo=home-assistant)
![Données](https://img.shields.io/badge/donn%C3%A9es-API%20SNCF%20(Navitia)-yellow.svg?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)

Package **Home Assistant** qui affiche les **trois prochains TER au départ de la gare de Basse-Indre**, dans chaque sens (**Savenay** et **Nantes**), avec heure théorique, retard et fraîcheur de la donnée. Une seule requête API par minute.

> [!IMPORTANT]
> **En bref**
> - Données : API SNCF / Navitia (`api.sncf.com`), **jeton gratuit requis** (inscription sur le portail SNCF).
> - **Un seul appel `/departures` par minute** : il renvoie les deux sens ; le tri Savenay / Nantes se fait ensuite dans des capteurs `template` (aucun appel supplémentaire).
> - Le jeton ne figure **jamais** dans le dépôt : il est lu dans `secrets.yaml`, sous la forme d'un en-tête `Authorization` **pré-encodé en base64** (contournement d'un défaut d'`authentication: basic` avec `!secret`, voir plus bas).

---

## Ce que ça fait

| Capteur | Contenu |
| :--- | :--- |
| `sensor.sncf_departs_basse_indre_raw` | Réponse brute de l'API (attribut `departures`), état = nombre de départs |
| `sensor.sncf_train_basse_indre_1` … `_3` | 3 prochains départs **sens Savenay** |
| `sensor.sncf_train_basse_indre_nantes_1` … `_3` | 3 prochains départs **sens Nantes** |

État de chaque capteur : l'heure de départ réelle (`18:05`), ou `N/A` s'il n'y a pas de train. Attributs : `destination`, `numero`, `heure_theorique`, `en_retard` (booléen), `retard_minutes`, `data_freshness` (`realtime` ou `base_schedule`).

**Fonctionnement** : le capteur `rest` interroge `stop_area:SNCF:87481069` (Basse-Indre) ; les capteurs `template` filtrent sur `display_informations.direction` (contient « Nantes » ou non).

---

## Installation

1. Obtenir un jeton sur le portail développeur SNCF.
2. Calculer l'en-tête : `echo -n "VOTRE_JETON:" | base64`, puis ajouter dans `/config/secrets.yaml` :
   `sncf_api_token_b64: "Basic <résultat>"` (voir `examples/secrets.example.yaml`).
3. Copier `packages/sncf_basse_indre.yaml` dans `/config/packages/` (`homeassistant: packages: !include_dir_named packages`).
4. Vérifier la configuration, puis redémarrer Home Assistant.

> [!NOTE]
> Si le jeton est régénéré, il faut **recalculer** le secret (l'encodage base64 est fait à la main, ce n'est pas une simple substitution).

### Pourquoi un en-tête pré-encodé ?
Avec `authentication: basic` + `username: !secret …`, le composant `rest` n'a pas transmis le jeton (réponse « no token »), alors que le même secret fonctionne dans un en-tête classique. Le contournement est vérifié fonctionnel (voir CHANGELOG 2.0.0).

---

## Adapter à une autre gare

1. Trouver l'identifiant `stop_area:SNCF:XXXXXXXX` de la gare (l'UIC, avec le préfixe `stop_area:SNCF:`).
2. Le remplacer dans `resource`.
3. Adapter le filtre de sens (`'Nantes'`) à une direction de ton réseau.

---

## Tests

```
pip install -r requirements_test.txt
pytest -v
```
Tests statiques (aucun Home Assistant requis) : clés YAML dupliquées, jeton lu depuis un secret, identifiants uniques, cadence ≥ 60 s, attributs homogènes, et **rendu des gabarits** sur un jeu de données d'exemple (`examples/sample_departures.json`) : séparation des sens, retard calculé, valeurs par défaut.

---

## Licence
MIT – voir `LICENSE`.
