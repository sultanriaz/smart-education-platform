from pathlib import Path

from smartedu_perf import parse_locust_stats


def test_locust_csv_parser(tmp_path: Path):
    path = tmp_path / "stats.csv"
    path.write_text(
        "Type,Name,Request Count,Failure Count,Median Response Time,"
        "Average Response Time,Min Response Time,Max Response Time,"
        "Average Content Size,Requests/s,Failures/s,50%,95%,99%\n"
        "GET,/api/v1/attendance/sessions,100,1,400,500,10,2000,"
        "123,20.0,0.2,400,900,1500\n"
        ",Aggregated,100,1,400,500,10,2000,123,20.0,0.2,400,900,1500\n",
        encoding="utf-8",
    )

    rows = parse_locust_stats(path)
    assert len(rows) == 1
    assert rows[0].name == "/api/v1/attendance/sessions"
    assert rows[0].p95_ms == 900
    assert rows[0].error_rate == 0.01
