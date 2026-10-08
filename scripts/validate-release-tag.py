from __future__ import annotations
import argparse, subprocess
from smartedu_cicd import validate_release_tag

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("tag"); p.add_argument("--require-ancestor-of",default="origin/main"); a=p.parse_args(); validate_release_tag(a.tag)
 sha=subprocess.check_output(["git","rev-list","-n","1",a.tag],text=True).strip()
 if subprocess.run(["git","merge-base","--is-ancestor",sha,a.require_ancestor_of]).returncode: raise SystemExit(f"{a.tag} commit is not an ancestor of {a.require_ancestor_of}")
 print(f"release_tag={a.tag}"); print(f"commit_sha={sha}"); return 0
if __name__=="__main__": raise SystemExit(main())
