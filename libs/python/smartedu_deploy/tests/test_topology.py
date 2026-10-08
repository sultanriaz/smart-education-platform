from smartedu_deploy import ProductionTopology


def test_topology_requires_unique_workloads_and_replica_floor():
    topology = ProductionTopology.model_validate(
        {
            "public_host": "smartedu.example.edu",
            "tls_secret_name": "smartedu-tls",
            "workloads": [
                {
                    "component": "identity-service",
                    "kind": "python-service",
                    "port": 8000,
                    "replicas": 2,
                    "min_replicas": 2,
                    "max_replicas": 4,
                    "resources": {
                        "cpu_request": "100m",
                        "memory_request": "256Mi",
                        "cpu_limit": "500m",
                        "memory_limit": "512Mi",
                    },
                }
            ],
            "external_dependencies": [],
        }
    )
    assert topology.workloads[0].replicas == 2
