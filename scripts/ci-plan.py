from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path
from smartedu_cicd import affected_components, load_catalog

def changed_files(base: str, head: str) -> list[str]:
    cp=subprocess.run(["git","diff","--name-only",f"{base}...{head}"],check=True,capture_output=True,text=True)
    return [x.strip() for x in cp.stdout.splitlines() if x.strip()]

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--catalog",default="config/cicd/components.yaml"); p.add_argument("--base"); p.add_argument("--head",default="HEAD"); p.add_argument("--all",action="store_true"); p.add_argument("--github-output"); a=p.parse_args()
    catalog=load_catalog(a.catalog); files=[] if a.all else changed_files(a.base or "HEAD~1",a.head); selected=list(catalog.components) if a.all else affected_components(catalog,files)
    rows=[{"name":x.name,"kind":x.kind,"path":x.path,"context":x.build_context,"dockerfile":x.dockerfile,"image_suffix":x.image_suffix} for x in selected]
    service_rows=[x for x in rows if x["kind"]=="python-service"]
    outputs={"all":json.dumps({"include":rows},separators=(",",":")),"services":json.dumps({"include":service_rows},separators=(",",":")),"has_services":str(bool(service_rows)).lower(),"frontend_changed":str(any(x.name=="frontend" for x in selected)).lower(),"gateway_changed":str(any(x.name=="api-gateway" for x in selected)).lower(),"changed_count":str(len(selected))}
    if a.github_output:
        with Path(a.github_output).open("a",encoding="utf-8") as f:
            for k,v in outputs.items(): f.write(f"{k}={v}\n")
    else: print(json.dumps(outputs,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
