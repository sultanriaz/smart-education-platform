from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_secret_example_is_not_in_kustomization():
    kustomization = yaml.safe_load(
        (
            ROOT
            / "deploy"
            / "kubernetes"
            / "production"
            / "kustomization.yaml"
        ).read_text(encoding="utf-8")
    )
    assert "secrets.example.yaml" not in kustomization["resources"]


def test_example_secrets_have_no_real_looking_credentials():
    path = (
        ROOT
        / "deploy"
        / "kubernetes"
        / "production"
        / "secrets.example.yaml"
    )
    for doc in yaml.safe_load_all(path.read_text(encoding="utf-8")):
        if not isinstance(doc, dict):
            continue
        for value in doc.get("stringData", {}).values():
            assert "REPLACE" in value
