import bpy,sys,pathlib,ast,json,numpy as np
from mathutils import Matrix,Vector,Quaternion
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from inspect_native import *
ROOT=pathlib.Path(__file__).resolve().parents[1]
REF=GAME/'media/models_X/Skinned/Raccoon_Body.x'
FF=frames(REF);OFF=skin_offsets(REF);BW={n:Matrix(np.linalg.inv(m).tolist()) for n,m in OFF.items()}
for n,f in FF.items():
    if n=='Raccoon':continue
    if n not in BW:BW[n]=BW[f['parent']]@Matrix(f['local'].tolist()) if f['parent'] in BW else Matrix(f['global'].tolist())
C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)));Q=Matrix(((0,1,0,0),(-1,0,0,0),(0,0,1,0),(0,0,0,1)))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/EwingsCat_Adult.blend'))
obj=bpy.data.objects['EwingsCat_Adult_BrownTabby'];rig=bpy.data.objects['CompatibilityRig']
tree=ast.parse((ROOT/'tools/build_cat.py').read_text());sel=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['sample','apply_native_pose']];exec(compile(ast.Module(body=sel,type_ignores=[]),'pose_functions','exec'))
samples=[]
for clip,fraction in [(c,f) for c in ['Rac_Idle01.x','Rac_Walk.x','Rac_Run.x','Rac_IdleLyingDown.x'] for f in [0,.25,.5,.75,1]]:
    pose=apply_native_pose(GAME/'media/anims_X/Raccoon'/clip,fraction)
    aw=apply_native_pose.last_aw
    errors=[]
    for n in OFF:
        desired=C@aw[n]@Q
        errors.append((max(abs(rig.pose.bones[n].matrix[i][j]-desired[i][j]) for i in range(4) for j in range(4)),n))
    maxbone=max(e for e,n in errors)
    dg=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dg);me=ev.to_mesh();errs=[]
    for i,v in enumerate(obj.data.vertices):
        oracle=Vector((0,0,0))
        for g in v.groups:
            n=obj.vertex_groups[g.group].name
            oracle+=(C@aw[n]@BW[n].inverted()@C.inverted()@v.co)*g.weight
        errs.append((me.vertices[i].co-oracle).length)
    ev.to_mesh_clear()
    maxrest=max(max(abs(rig.data.bones[n].matrix_local[i][j]-(C@BW[n]@Q)[i][j]) for i in range(4) for j in range(4)) for n in OFF)
    assert max(errs)<1e-4 and maxbone<1e-4 and maxrest<2e-6
    samples.append(dict(pose,lbs_oracle_max_error=max(errs),bone_matrix_max_error=maxbone,bind_matrix_max_error=maxrest))
report={'sample_count':len(samples),'clips':4,'max_influences':max(len(v.groups) for v in obj.data.vertices),'all_passed':True,'max_lbs_error':max(p['lbs_oracle_max_error'] for p in samples),'samples':samples,'limit':'Independent linear skinning math and Blender CPU deformation only, not game rendering.'}
(ROOT/'verification/rig_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('RIG_VALIDATION_OK',report['sample_count'],report['max_lbs_error'])
