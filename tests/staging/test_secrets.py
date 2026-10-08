from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "deploy" / "kubernetes" / "staging"


def test_example_secrets_are_not_part_of_kustomization():
    payload = yaml.safe_load(
        (STAGING / "kustomization.yaml").read_text(encoding="utf-8")
    )
    assert "secrets.example.yaml" not in payload["resources"]


def test_secret_examples_only_contain_placeholders():
    for doc in yaml.safe_load_all(
        (STAGING / "secrets.example.yaml").read_text(encoding="utf-8")
    ):
        if not isinstance(doc, dict):
            continue
        for value in doc.get("stringData", {}).values():
            assert "REPLACE" in value
