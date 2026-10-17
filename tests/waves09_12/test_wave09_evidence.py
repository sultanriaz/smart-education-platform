"""Wave9 negative tests: missing/insufficient load evidence must not be marked PASS."""
import csv
import importlib.util
from pathlib import Path
import pytest

MOD = Path(__file__).resolve().parents[2] / "scripts" / "wave09_12_acceptance.py"
spec = importlib.util.spec_from_file_location("wave09_12_acceptance", MOD)
gates = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gates)


def make_csv(prefix, sample_users=500, count=10):
    p = Path(str(prefix) + "_stats.csv")
    with p.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Request Count", "Failure Count", "95%"])
        writer.writeheader();writer.writerow({"Name":"Aggregated", "Request Count":1000,
            "Failure Count":0,"95%":900})
    h=Path(str(prefix)+"_stats_history.csv")
    with h.open("w", newline="") as f:
        writer=csv.DictWriter(f, fieldnames=["Timestamp","User Count"]);writer.writeheader()
        for i in range(count):writer.writerow({"Timestamp":100000+i*10,"User Count":sample_users})


def test_missing_locust_evidence_is_blocked(tmp_path):
    with pytest.raises(ValueError, match="Missing Locust"):
        gates.evaluate_csv(tmp_path / "missing", users=500, seconds=900)


def test_one_sample_at_500_cannot_claim_capacity(tmp_path):
    prefix=tmp_path / "short";make_csv(prefix)
    actual=gates.evaluate_csv(prefix,users=500,seconds=900)
    assert actual["statuses"]["D20"]=="BLOCKED"  # no real browser page timing
    assert actual["statuses"]["D21"]=="BLOCKED"


def test_sustained_500_user_timeline_required(tmp_path):
    prefix=tmp_path / "long";make_csv(prefix,count=92)
    actual=gates.evaluate_csv(prefix,users=500,seconds=910)
    assert actual["observed_sustained_500_seconds"]>=900
    assert actual["statuses"]["D21"]=="PASS"


def test_no_benchmark_request_cannot_pass(tmp_path):
    prefix=tmp_path / "empty";make_csv(prefix)
    text=Path(str(prefix)+"_stats.csv").read_text().replace("1000,0,900","0,0,900")
    Path(str(prefix)+"_stats.csv").write_text(text)
    with pytest.raises(ValueError, match="Zero requests"):
        gates.evaluate_csv(prefix,users=500,seconds=900)
