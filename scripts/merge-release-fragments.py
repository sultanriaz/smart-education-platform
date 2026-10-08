from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
from smartedu_cicd import ReleaseImage, ReleaseManifest, load_catalog

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("--fragments",required=True); p.add_argument("--catalog",default="config/cicd/components.yaml"); p.add_argument("--tag",required=True); p.add_argument("--commit",required=True); p.add_argument("--repository",required=True); p.add_argument("--migration-components",default=""); p.add_argument("--output",required=True); a=p.parse_args()
 images=[ReleaseImage.model_validate(json.loads(x.read_text(encoding="utf-8"))) for x in sorted(Path(a.fragments).rglob("*.json"))]
 expected={x.name for x in load_catalog(a.catalog).components}; found={x.component for x in images}
 if found!=expected: raise SystemExit(f"release fragments mismatch missing={sorted(expected-found)} extra={sorted(found-expected)}")
 manifest=ReleaseManifest(release_tag=a.tag,commit_sha=a.commit,generated_at=datetime.now(timezone.utc).isoformat(),source_repository=a.repository,images=sorted(images,key=lambda x:x.component),migration_policy="forward-only",migration_components=[x.strip() for x in a.migration_components.split(",") if x.strip()])
 Path(a.output).write_text(json.dumps(manifest.model_dump(),indent=2)+"\n",encoding="utf-8"); print(a.output); return 0
if __name__=="__main__": raise SystemExit(main())
