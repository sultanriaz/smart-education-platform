from __future__ import annotations
import argparse,time,urllib.request

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("url"); p.add_argument("--timeout",type=int,default=120); p.add_argument("--interval",type=float,default=2); a=p.parse_args(); deadline=time.monotonic()+a.timeout; last=""
 while time.monotonic()<deadline:
  try:
   with urllib.request.urlopen(a.url,timeout=5) as r:
    if r.status==200: print(f"PASS {a.url}"); return 0
    last=str(r.status)
  except Exception as exc: last=str(exc)
  time.sleep(a.interval)
 print(f"FAIL {a.url}: {last}"); return 1
if __name__=="__main__": raise SystemExit(main())
