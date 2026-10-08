"""Contrôles statiques du package SNCF (aucun Home Assistant requis)."""
import collections
import json
import pathlib
import re

import jinja2
import pytest
import yaml

ROOT = pathlib.Path(__file__).parent.parent
PKG = ROOT / "packages" / "sncf_basse_indre.yaml"
SAMPLE = ROOT / "examples" / "sample_departures.json"


class StrictLoader(yaml.SafeLoader):
    """Refuse les clés dupliquées et comprend !secret."""


def _mapping(loader, node, deep=False):
    keys = [loader.construct_object(k, deep=deep) for k, _ in node.value]
    dup = [k for k, n in collections.Counter(keys).items() if n > 1]
    if dup:
        raise ValueError(f"clés dupliquées : {dup}")
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)
StrictLoader.add_constructor("!secret", lambda l, n: f"SECRET:{l.construct_scalar(n)}")


@pytest.fixture(scope="module")
def cfg():
    return yaml.load(PKG.read_text(encoding="utf-8"), Loader=StrictLoader)


def sensors(cfg):
    return cfg["template"][0]["sensor"]


def test_no_duplicate_keys_and_parses(cfg):
    assert "rest" in cfg and "template" in cfg


def test_token_comes_from_secret(cfg):
    assert cfg["rest"][0]["headers"]["Authorization"] == "SECRET:sncf_api_token_b64"
    assert "Basic " not in PKG.read_text(encoding="utf-8")


def test_unique_ids_and_count(cfg):
    ids = [s["unique_id"] for s in sensors(cfg)]
    ids.append(cfg["rest"][0]["sensor"][0]["unique_id"])
    assert len(ids) == len(set(ids)) == 7


def test_one_api_call_per_minute(cfg):
    assert cfg["rest"][0]["scan_interval"] >= 60
    assert "/departures" in cfg["rest"][0]["resource"]


def test_all_sensors_have_same_attributes(cfg):
    expected = {"destination", "numero", "heure_theorique", "en_retard", "retard_minutes", "data_freshness"}
    for s in sensors(cfg):
        assert set(s["attributes"]) == expected, s["unique_id"]


# --- rendu des gabarits avec des données d'exemple -------------------------
def _env(data):
    env = jinja2.Environment()
    env.tests["search"] = lambda v, p: re.search(p, str(v)) is not None
    env.globals["state_attr"] = lambda e, a: data
    return env


def render(tpl, data):
    return _env(data).from_string(tpl).render().strip()


def by_id(cfg, uid):
    return next(s for s in sensors(cfg) if s["unique_id"] == uid)


def test_direction_split_and_delay(cfg):
    data = json.loads(SAMPLE.read_text())["departures"]
    sav, nan = by_id(cfg, "sncf_train_bi_1"), by_id(cfg, "sncf_train_bi_nantes_1")
    assert render(sav["state"], data) == "18:05"
    assert render(sav["attributes"]["destination"], data) == "Savenay"
    assert render(sav["attributes"]["en_retard"], data) == "True"
    assert render(sav["attributes"]["retard_minutes"], data) == "5"
    assert render(nan["state"], data) == "18:10"
    assert render(nan["attributes"]["en_retard"], data) == "False"


def test_missing_departures_give_placeholders(cfg):
    data = json.loads(SAMPLE.read_text())["departures"]
    assert render(by_id(cfg, "sncf_train_bi_3")["state"], data) == "N/A"
    assert render(by_id(cfg, "sncf_train_bi_3")["attributes"]["destination"], data) == "–"
    assert render(by_id(cfg, "sncf_train_bi_nantes_1")["state"], []) == "N/A"
