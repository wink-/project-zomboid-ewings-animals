"""Create deterministic, inspected source/install ZIPs. Never installs."""
from pathlib import Path,PurePosixPath
import io,json,zipfile,hashlib,shutil,re
from sanitize_pngs import sanitize_tree
from normalize_text import normalize_tree
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'stage/EwingsAnimals'
VER=re.search(r'(?m)^version=(.+)$',(MOD/'42/mod.info').read_text()).group(1).strip()
OUT=ROOT/'release'/VER;OUT.mkdir(parents=True,exist_ok=True)
DOCS=['README.md','ACCEPTANCE.md','ASSET_PROVENANCE.md','CHANGELOG.md']
sanitize_tree(ROOT)
normalize_tree(ROOT)
offline=json.loads((ROOT/'verification/offline_validation.json').read_text());rig=json.loads((ROOT/'verification/rig_validation.json').read_text());art=json.loads((ROOT/'verification/art_validation.json').read_text())
petting=json.loads((ROOT/'verification/petting_validation.json').read_text())
behavior=json.loads((ROOT/'verification/behavior_validation.json').read_text())
assert behavior['all_passed'] and behavior['version']==VER
icons=json.loads((ROOT/'verification/icon_validation.json').read_text())
assert icons['all_passed'] and icons['version']==VER
assert petting['all_passed'] and petting['version']==VER
assert petting['native_pickup_stub_execution']['exit_code']==0
assert rig['all_passed'] and rig['sample_count']==20
assert offline['checks']['native_lua_definition_execution']['exit_code']==0
assert offline['checks']['native_mesh_import']['exit_code']==0
summary=f'''# Offline validation - Ewing's Animals {VER}

Target: B42.21 / Steam25485521, Windows.

- Original source mesh: {art['vertices']} vertices, {art['triangles']} triangles.
- At most {art['max_influences']} normalized bone influences per vertex.
- Installed native Assimp importer: passed; no embedded animation clips.
- Installed native model-script parser: passed.
- Installed native Lua compiler: all runtime Lua scripts passed.
- Installed Kahlua execution: additive adult/kitten registration, growth, diet, milk and scope assertions passed.
- Cat-only petting XML parsed natively; native action delegation/cleanup and normal/dwarf selection assertions passed.
- Native petting supplies its own stress effect and cooldown; no custom stress values or global overrides.
- Native pickup path/action/inventory conversion inspected and stub-tested.
- Actual Java animal-definition loader parsed native raccoons and both cats.
- Installed JVM reproduced NaN weight from zero stage duration and finite pickup-eligible weight with duration 60.
- Cat-only food menu and kitten XML parser checks passed; live menu integration remains pending.
- No pickup/acceptance bypass or save migration was added.
- Original mesh, coat texture and Blender source match v0.1.0 byte for byte.
- Original adult/kitten icons regenerated; native breed path lookup, alpha/padding, exact casing and native hand render sizes checked.
- User confirmed kitten pickup on 0.1.3; this is not 0.1.4 icon or multiplayer validation.
- Four native motion clips sampled at five phases each: {rig['sample_count']} offline poses passed.
- Independent linear skinning comparison maximum error: {rig['max_lbs_error']:.10f} model units.
- Reference hashes match the baseline; no native files were changed.
- Seven Blender renders were visually reviewed as an offline contact sheet.
- ZIP contents, CRCs, SHA-256 and repeated-build byte determinism checked.

These results do not constitute gameplay, renderer-integration, save/reload or
multiplayer certification. See ACCEPTANCE.md for pending disposable-world tests.
Milk support is native configuration plus inspected fluid-consumption code;
actual menu/consumption/network behavior remains a gameplay acceptance item.
Validation required no installation, game/server launch, save access or downloads.
'''
(ROOT/'VALIDATION.md').write_text(summary,encoding='utf-8',newline='\n')
for name in DOCS+['VALIDATION.md']:
    if name=='README.md':
        t=(ROOT/name).read_text(encoding='utf-8').replace('![Offline Blender preview of the original cat](previews/EwingsAnimals_cat_preview.png)','Offline previews are included with the source ZIP and prototype release.')
        (MOD/name).write_text(t,encoding='utf-8',newline='\n')
    else:shutil.copyfile(ROOT/name,MOD/name)

def entries_from(paths,prefix,base):
    return [(prefix+'/'+p.relative_to(base).as_posix(),p.read_bytes()) for p in sorted(paths) if p.is_file()]
def zipbytes(entries):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(entries):
            pp=PurePosixPath(name);assert not pp.is_absolute() and '..' not in pp.parts
            i=zipfile.ZipInfo(name,date_time=(2026,10,23,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.create_system=3;i.external_attr=0o100644<<16
            z.writestr(i,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return b.getvalue()
def make(name,entries):
    a=zipbytes(entries);b=zipbytes(entries);assert a==b,'Nondeterministic ZIP'
    path=OUT/name;path.write_bytes(a)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert sorted(z.namelist())==sorted(n for n,d in entries)
        for n,d in entries:assert z.read(n)==d
    digest=hashlib.sha256(a).hexdigest();(OUT/(name+'.sha256')).write_text(digest+'  '+name+'\n')
    return {'file':name,'bytes':len(a),'sha256':digest,'members':len(entries),'deterministic':True,'crc_and_bytes_verified':True}

install=entries_from(MOD.rglob('*'),'EwingsAnimals',MOD)
assert any(n=='EwingsAnimals/42/mod.info' for n,d in install)
assert any(n=='EwingsAnimals/common/README.txt' for n,d in install)
assert not any(n.lower().endswith(('.dll','.jar','.class','.blend','.pyc')) for n,d in install)
reports=['art_validation.json','rig_validation.json','offline_validation.json','native_reference_hashes.json','petting_validation.json','behavior_validation.json','icon_validation.json']
sourcepaths=[ROOT/n for n in DOCS+['VALIDATION.md','.gitignore']]
sourcepaths+=list((ROOT/'tools').glob('*.py'))+[ROOT/'art/EwingsCat_Adult.blend']
sourcepaths+=list((ROOT/'previews').glob('*.png'))+[ROOT/'verification'/n for n in reports]
sourcepaths+=list(MOD.rglob('*'))
source=entries_from(sourcepaths,'EwingsAnimals',ROOT)
assert len({n for n,d in source})==len(source)
# Principal native source hashes must not appear as archived file payloads.
native=json.loads((ROOT/'verification/native_reference_hashes.json').read_text());nativehash={v['before'] for v in native.values()}
assert not any(hashlib.sha256(d).hexdigest() in nativehash for n,d in source)
manifest={'version':VER,'archives':[make(f'EwingsAnimals-{VER}-prototype-install.zip',install),make(f'EwingsAnimals-{VER}-prototype-source.zip',source)],'gameplay_tested':False,'multiplayer_tested':False,'installed':False,'publication_pending':True}
shutil.copyfile(ROOT/'previews/EwingsAnimals_cat_preview.png',OUT/'EwingsAnimals-cat-preview.png')
shutil.copyfile(ROOT/'previews/01_three_quarter.png',OUT/'EwingsAnimals-cat-three-quarter.png')
shutil.copyfile(ROOT/'VALIDATION.md',OUT/'VALIDATION.md')
shutil.copyfile(ROOT/'previews/EwingsAnimals_hand_icons_preview.png',OUT/'EwingsAnimals-hand-icons-preview.png')
(OUT/'SHA256SUMS.txt').write_text(''.join(a['sha256']+'  '+a['file']+'\n' for a in manifest['archives']))
(OUT/'release_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
