from __future__ import annotations
import argparse, json
from pathlib import Path
from smartedu_cicd import ReleaseManifest, load_catalog, validate_release_tag

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("manifest"); p.add_argument("--catalog",default="config/cicd/components.yaml"); a=p.parse_args(); m=ReleaseManifest.model_validate(json.loads(Path(a.manifest).read_text(encoding="utf-8"))); validate_release_tag(m.release_tag)
 expected={x.name for x in load_catalog(a.catalog).components}; found={x.component for x in m.images}
 if expected!=found: raise SystemExit(f"manifest mismatch missing={sorted(expected-found)} extra={sorted(found-expected)}")
 for image in m.images:
  if image.immutable_ref != f"{image.repository}@{image.digest}": raise SystemExit(f"{image.component}: immutable_ref mismatch")
 print(f"PASS {m.release_tag}: {len(m.images)} digest-pinned images"); return 0
if __name__=="__main__": raise SystemExit(main())
