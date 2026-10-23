"""Check final publication ZIPs for excluded payloads and local paths."""
from pathlib import Path
import zipfile,re,json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'release';checks=[]
for path in sorted(OUT.glob('*.zip')):
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            low=name.lower();data=z.read(name)
            assert not any(x in low for x in ['.library-transfer','/probes/','/.git/','__pycache__'])
            assert not low.endswith(('.dll','.jar','.class','.pyc','.blend1','.log'))
            assert not re.search(rb'[A-Za-z]:[\\/]Users[\\/]',data),name+' contains a user path'
            assert not re.search(rb'DESKTOP-[A-Z0-9]{5,}',data),name+' contains a local hostname'
            assert not any(k in data for k in [('gh'+'p_').encode(),('github'+'_pat_').encode()]),name+' contains a credential marker'
            if low.endswith('.x'):assert low.endswith('/ewingscat_adult.x'),name
        assert z.testzip() is None
    checks.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'private_path_and_payload_scan':'passed'})
print(json.dumps(checks,indent=2))
