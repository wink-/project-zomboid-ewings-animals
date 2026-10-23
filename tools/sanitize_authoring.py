"""Remove local paths from the original .blend without changing geometry."""
import bpy,pathlib,hashlib,struct,json,re
ROOT=pathlib.Path(__file__).resolve().parents[1];path=ROOT/'art/EwingsCat_Adult.blend'
def geometry_hash():
    obj=bpy.data.objects['EwingsCat_Adult_BrownTabby'];b=bytearray()
    for v in obj.data.vertices:
        b.extend(struct.pack('<3f',*v.co))
        for g in v.groups:b.extend(struct.pack('<If',g.group,g.weight))
    for p in obj.data.polygons:
        for i in p.vertices:b.extend(struct.pack('<I',i))
    return hashlib.sha256(b).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(path));before=geometry_hash()
for image in bpy.data.images:
    if image.name=='EwingsCat_BrownTabby':
        image.filepath='//../stage/EwingsAnimals/42/media/textures/Body/EwingsCat_BrownTabby.png'
        if not image.packed_file:image.pack()
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
assert all(not a.animation_data or not a.animation_data.action for a in bpy.data.objects)
assert not bpy.data.actions
assert geometry_hash()==before
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=False)
# Blender's fixed-width FileGlobal filename may retain the save location.
# Replace only the exact serialized current filename, preserving every byte
# offset and field width. The file is reopened and its geometry checked below.
raw=path.read_bytes();count=0
for filename in {str(path),path.as_posix()}:
    old=filename.encode();new=path.name.encode()
    count+=raw.count(old);raw=raw.replace(old,new+b'\0'*(len(old)-len(new)))
# Packed-image origin fields and file-browser defaults are also fixed-width
# metadata. Remove only complete printable paths rooted in this user's home.
home={str(pathlib.Path.home()).encode(),pathlib.Path.home().as_posix().encode()}
for old in set(re.findall(rb'[\x20-\x7e]{8,}',raw)):
    if not any(old.startswith(h) for h in home):continue
    new=b'//../stage/EwingsAnimals/42/media/textures/Body/EwingsCat_BrownTabby.png' if old.endswith(b'EwingsCat_BrownTabby.png') else b'.'
    if len(new)>len(old):new=b'.'
    count+=raw.count(old);raw=raw.replace(old,new+b'\0'*(len(old)-len(new)))
assert b'Users\\' not in raw and b'Users/' not in raw, 'An unresolved user path remains'
path.write_bytes(raw)
bpy.ops.wm.open_mainfile(filepath=str(path));after=geometry_hash();assert before==after
assert not bpy.data.actions
report={'geometry_sha256_before':before,'geometry_sha256_after':after,'unchanged_geometry':True,'local_filename_fields_sanitized':count,'embedded_native_actions':0,'remaining_libraries':len(bpy.data.libraries)}
(ROOT/'verification/authoring_sanitization.json').write_text(json.dumps(report,indent=2)+'\n')
print('AUTHORING_SANITIZATION_OK',json.dumps(report))
