"""Normalize project-owned publication text to UTF-8/LF, preserving content."""
from pathlib import Path
def normalize_tree(root):
    root=Path(root)
    paths=[root/n for n in ['.gitignore','README.md','ACCEPTANCE.md','ASSET_PROVENANCE.md','CHANGELOG.md','VALIDATION.md']]
    paths+=list((root/'tools').glob('*.py'))
    paths+=[p for p in (root/'stage').rglob('*') if p.is_file() and (p.suffix.lower() in {'.lua','.json','.txt','.x','.xml','.md','.info'})]
    paths+=[root/'verification'/n for n in ['art_validation.json','rig_validation.json','offline_validation.json','native_reference_hashes.json','petting_validation.json','behavior_validation.json']]
    for path in paths:
        if not path.exists():continue
        b=path.read_bytes()
        try:t=b.decode('utf-8')
        except UnicodeDecodeError:t=b.decode('cp1252')
        t='\n'.join(line.rstrip(' \t') for line in t.replace('\r\n','\n').replace('\r','\n').split('\n')).rstrip()+'\n'
        path.write_bytes(t.encode('utf-8'))
if __name__=='__main__':normalize_tree(Path(__file__).resolve().parents[1]);print('PUBLICATION_TEXT_NORMALIZED')
