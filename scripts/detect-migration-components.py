from __future__ import annotations
import argparse, subprocess
from smartedu_cicd import load_catalog

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("--tag",required=True); p.add_argument("--catalog",default="config/cicd/components.yaml"); a=p.parse_args(); c=load_catalog(a.catalog)
 tags=subprocess.check_output(["git","tag","--sort=-creatordate"],text=True).splitlines(); previous=next((t for t in tags if t!=a.tag),None)
 if not previous: print(""); return 0
 files=subprocess.check_output(["git","diff","--name-only",previous,a.tag],text=True).splitlines(); changed=[]
 for x in c.components:
  if x.kind!="python-service": continue
  prefix=x.path.rstrip("/")+"/"
  if any(f.startswith(prefix) and ("/migrations/" in f or "/alembic/versions/" in f or f.endswith("alembic.ini")) for f in files): changed.append(x.name)
 print(",".join(sorted(changed))); return 0
if __name__=="__main__": raise SystemExit(main())
