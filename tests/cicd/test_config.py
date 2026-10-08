from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
def test_catalog():
 p=yaml.safe_load((ROOT/'config/cicd/components.yaml').read_text()); assert len(p['components'])==12; assert sum(x['kind']=='python-service' for x in p['components'])==10
def test_release_policy():
 p=yaml.safe_load((ROOT/'config/cicd/release-policy.yaml').read_text()); assert p['image_policy']['allow_latest_tag'] is False; assert p['image_policy']['require_digest'] is True; assert p['image_policy']['sign_images'] is True
