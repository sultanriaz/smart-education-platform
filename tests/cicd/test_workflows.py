from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
def test_workflows_parse():
 paths=sorted((ROOT/'.github/workflows').glob('*.yml')); assert paths
 for p in paths: yaml.safe_load(p.read_text())
def test_release_has_supply_chain_controls():
 t=(ROOT/'.github/workflows/release.yml').read_text(); assert 'sbom: true' in t; assert 'provenance: mode=max' in t; assert 'cosign sign' in t; assert ':latest' not in t
def test_staging_uses_protected_environment_and_self_hosted():
 t=(ROOT/'.github/workflows/staging-deploy.yml').read_text(); assert 'environment: staging' in t; assert 'self-hosted' in t; assert 'verify-release-signatures.py' in t
