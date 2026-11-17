import json
import urllib.request
import hashlib
from pathlib import Path

reg = json.loads(Path("registry.json").read_text(encoding="utf-8"))

print(f"Checking all {len(reg['extensions'])} extensions live on GitHub:")
all_ok = True

for ext in reg["extensions"]:
    eid = ext["id"]
    d_url = ext["download_url"]
    i_url = ext["icon_url"]
    exp_sha = ext["sha256"]
    
    # Download check
    try:
        req = urllib.request.Request(d_url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req).read()
        d_sha = hashlib.sha256(data).hexdigest()
        d_ok = (d_sha == exp_sha)
        d_status = "200 (SHA OK)" if d_ok else f"SHA MISMATCH ({d_sha[:8]} vs {exp_sha[:8]})"
    except Exception as e:
        d_ok = False
        d_status = f"ERR: {e}"
        
    # Icon check
    try:
        req = urllib.request.Request(i_url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req)
        i_ok = (resp.status == 200)
        i_status = "200 OK"
    except Exception as e:
        i_ok = False
        i_status = f"ERR: {e}"
        
    ok = d_ok and i_ok
    if not ok:
        all_ok = False
    status_str = "[PASS]" if ok else "[FAIL]"
    print(f"{status_str} {eid:18} | download: {d_status} | icon: {i_status}")

print("\nOverall GitHub live check:", "100% PERFECT ALL PASSED" if all_ok else "SOME ISSUES DETECTED")
