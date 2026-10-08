from pathlib import Path

import jsonschema
import yaml
import json

ROOT = Path(__file__).parent
SCHEMA = json.loads((ROOT / "workflow.schema.json").read_text(encoding="utf-8"))


def test_all_workflow_specs_are_valid():
    files = sorted(ROOT.glob("*.yaml"))
    assert files, "No workflow specifications found"
    for path in files:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(SCHEMA).validate(payload)


def test_all_three_roles_have_workflows():
    actors = {
        yaml.safe_load(path.read_text(encoding="utf-8"))["actor"]
        for path in ROOT.glob("*.yaml")
    }
    assert actors == {"student", "teacher", "admin"}
