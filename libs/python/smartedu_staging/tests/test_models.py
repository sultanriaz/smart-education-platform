import pytest

from smartedu_staging import StagingTopology


def test_staging_topology_requires_valid_scaling():
    topology = StagingTopology.model_validate(
        {
            "public_host": "staging.example.org",
            "workload_overrides": [
                {
                    "component": "identity-service",
                    "replicas": 2,
                    "min_replicas": 2,
                    "max_replicas": 4,
                }
            ],
            "required_secrets": ["identity-service-secrets"],
            "stateful_dependencies": ["postgresql"],
        }
    )
    assert topology.workload_overrides[0].replicas == 2


def test_invalid_scaling_is_rejected():
    with pytest.raises(ValueError):
        StagingTopology.model_validate(
            {
                "public_host": "staging.example.org",
                "workload_overrides": [
                    {
                        "component": "identity-service",
                        "replicas": 1,
                        "min_replicas": 2,
                        "max_replicas": 3,
                    }
                ],
                "required_secrets": [],
                "stateful_dependencies": [],
            }
        )
