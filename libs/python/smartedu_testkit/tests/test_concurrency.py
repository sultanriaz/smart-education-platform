from smartedu_testkit import run_concurrently


def test_concurrent_runner_releases_workers_together():
    result = run_concurrently(4, lambda index: index * 2)
    assert sorted(result.values) == [0, 2, 4, 6]
    assert result.errors == ()
