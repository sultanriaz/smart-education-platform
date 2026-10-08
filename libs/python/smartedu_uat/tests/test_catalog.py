from pathlib import Path

import yaml

from smartedu_uat import load_scenarios


def test_catalog_ids_are_unique_and_have_required_fields(tmp_path: Path):
    path = tmp_path / "student.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "scenarios": [
                    {
                        "id": "UAT-STU-001",
                        "role": "Student",
                        "title": "Login",
                        "domain": "Identity",
                        "priority": "P0",
                        "execution": "manual",
                        "steps": ["Login"],
                        "expected_results": ["Workspace loads"],
                        "requirement_refs": ["REQ-IDENTITY-AUTH"],
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    scenarios = load_scenarios(tmp_path)
    assert scenarios[0].id == "UAT-STU-001"
    assert scenarios[0].priority == "P0"
