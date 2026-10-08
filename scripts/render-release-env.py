from __future__ import annotations
import argparse, json, re
from pathlib import Path
from smartedu_cicd import ReleaseManifest

def env_name(name:str)->str: return re.sub(r"[^A-Z0-9]+","_",name.upper()).strip("_")+"_IMAGE"
def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("manifest"); p.add_argument("--output",default=".env.release"); a=p.parse_args(); m=ReleaseManifest.model_validate(json.loads(Path(a.manifest).read_text(encoding="utf-8")))
 lines=[f"SMARTEDU_RELEASE_TAG={m.release_tag}",f"SMARTEDU_RELEASE_COMMIT={m.commit_sha}"]+[f"{env_name(x.component)}={x.immutable_ref}" for x in m.images]
 Path(a.output).write_text("\n".join(lines)+"\n",encoding="utf-8"); print(a.output); return 0
if __name__=="__main__": raise SystemExit(main())
