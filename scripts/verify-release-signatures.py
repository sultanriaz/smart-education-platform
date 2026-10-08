from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path
from smartedu_cicd import ReleaseManifest

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("manifest"); p.add_argument("--repository",required=True); p.add_argument("--issuer",default="https://token.actions.githubusercontent.com"); a=p.parse_args(); m=ReleaseManifest.model_validate(json.loads(Path(a.manifest).read_text()))
 identity=rf"https://github\.com/{a.repository}/\.github/workflows/release\.yml@refs/tags/{m.release_tag}"
 for image in m.images:
  subprocess.run(["cosign","verify","--certificate-identity-regexp",identity,"--certificate-oidc-issuer",a.issuer,image.immutable_ref],check=True)
 return 0
if __name__=="__main__": raise SystemExit(main())
