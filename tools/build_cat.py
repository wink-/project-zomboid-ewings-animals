"""Original Ewing's Animals cat. Run with Blender --background --factory-startup.

Creates original geometry/UV/coat, aligns it to the installed rig's bind metadata,
and REFERENCES native motions for local previews only. No native mesh, texture,
sound or animation is copied into the deliverable.
"""
import bpy, math, sys, pathlib, json, re, hashlib
import numpy as np
from mathutils import Matrix, Vector, Quaternion
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from inspect_native import GAME, frames, skin_offsets, animation, sha

ROOT = pathlib.Path(__file__).resolve().parents[1]
MOD = ROOT/'stage/EwingsAnimals/42'
ASSETS=MOD/'media'
for p in [ASSETS/'models_X/Skinned',ASSETS/'textures/Body',ASSETS/'textures',ROOT/'art',ROOT/'previews',ROOT/'verification']:
    p.mkdir(parents=True,exist_ok=True)
REF=GAME/'media/models_X/Skinned/Raccoon_Body.x'
FF=frames(REF); OFF=skin_offsets(REF)
BW={n:Matrix(np.linalg.inv(m).tolist()) for n,m in OFF.items()}
# Supply unweighted hierarchy nodes from the installed frame hierarchy; skin
# bones are reconstructed from inverse bind data, not the displayed walk pose.
for n,f in FF.items():
    if n=='Raccoon': continue
    if n not in BW:
        if f['parent'] in BW: BW[n]=BW[f['parent']] @ Matrix(f['local'].tolist())
        else: BW[n]=Matrix(f['global'].tolist())
C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
Q=Matrix(((0,1,0,0),(-1,0,0,0),(0,0,1,0),(0,0,0,1)))
def native(v): return (C.inverted() @ Vector(v))[:]
def point(v): return C @ Vector(v)
def bp(n): return BW[n].translation.copy()

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

# One original atlas: four horizontal surface panels and a small palette strip.
W=1024;H=1024
yy,xx=np.mgrid[0:H,0:W];u=xx/W;v=yy/H
rng=np.random.default_rng(5653)
noise=rng.normal(0,0.009,(H,W,1))
pixels=np.ones((H,W,4),dtype=np.float32)
base=np.array([0.245,0.175,0.105]);cream=np.array([0.64,0.54,0.39]);dark=np.array([0.075,0.065,0.05])
for panel in range(4):
    mask=(v>=panel*.22)&(v<(panel+1)*.22)
    sv=(v-panel*.22)/.22
    # Body longitudinal transverse tabby marks; irregular paired narrow bands.
    stripe=np.exp(-((np.sin((u*8.5+0.18*np.sin(sv*12))*math.pi))/0.23)**2)
    flank=(0.32+0.68*np.abs(np.sin(sv*math.pi*2)))
    color=base[None,None,:]*(1-.48*stripe[:,:,None]*flank[:,:,None])
    under=np.exp(-((sv-.5)/.12)**4)[:,:,None]
    if panel==0: color=color*(1-under*.8)+cream*under*.8
    if panel==1: color=color*.93
    if panel==2: color=color*1.1
    if panel==3: color=color*.9
    pixels[mask,:3]=(color+noise)[mask]
palette=[(.76,.69,.55),(.30,.20,.16),(.62,.36,.36),(.085,.075,.065),(.64,.74,.22),(.015,.02,.012),(.88,.83,.69),(.48,.39,.27)]
for i,col in enumerate(palette):
    pixels[int(H*.90):,int(i*W/8):int((i+1)*W/8),:3]=col
img=bpy.data.images.new('EwingsCat_BrownTabby',width=W,height=H,alpha=True)
img.pixels.foreach_set(np.clip(pixels,0,1).ravel());img.filepath_raw=str(ASSETS/'textures/Body/EwingsCat_BrownTabby.png');img.file_format='PNG';img.save()
mat=bpy.data.materials.new('Original brown mackerel tabby');mat.use_nodes=True
nodes=mat.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=img
bsdf=nodes.get('Principled BSDF');mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=.88

verts=[];faces=[];uvs=[];weights=[]
def addv(pos,uv,ww):
    ww={k:float(v) for k,v in ww.items() if v>1e-8};s=sum(ww.values());ww={k:v/s for k,v in ww.items()}
    assert len(ww)<=4
    verts.append(tuple(point(pos)));uvs.append(uv);weights.append(ww);return len(verts)-1
def uvpanel(i,u,v): return (.025+.95*u,.008+i*.22+.202*v)
def pal(i): return ((i+.5)/8,.95)
def mix(a,b,t): return {a:1-t,b:t}
def blendz(z):
    if z<-.12:return mix('Bip01_Neck','Bip01_Spine',min(1,max(0,(z+.19)/.08)))
    return mix('Bip01_Spine','Bip01_Pelvis',min(1,max(0,(z+.11)/.16)))

def ellipsoid(center,scale,ww,seg=16,rings=10,panel=1,palette=None):
    # Closed UV ellipsoid. Separate caps avoid zero-area pole triangles.
    center=Vector(center);ids=[]
    for j in range(1,rings):
        ph=math.pi*j/rings;row=[]
        for i in range(seg+1):
            th=2*math.pi*i/seg
            p=center+Vector((scale[0]*math.sin(ph)*math.cos(th),scale[1]*math.cos(ph),scale[2]*math.sin(ph)*math.sin(th)))
            row.append(addv(p,pal(palette) if palette is not None else uvpanel(panel,i/seg,j/rings),ww))
        ids.append(row)
    top=addv(center+Vector((0,scale[1],0)),pal(palette) if palette is not None else uvpanel(panel,.5,0),ww)
    bot=addv(center-Vector((0,scale[1],0)),pal(palette) if palette is not None else uvpanel(panel,.5,1),ww)
    for i in range(seg):faces.append((top,ids[0][i+1],ids[0][i]));faces.append((bot,ids[-1][i],ids[-1][i+1]))
    for j in range(len(ids)-1):
        for i in range(seg):faces.extend([(ids[j][i],ids[j][i+1],ids[j+1][i+1]),(ids[j][i],ids[j+1][i+1],ids[j+1][i])])

def tube(points,radii,wws,seg=12,panel=2):
    ids=[]
    for j,p in enumerate(points):
        p=Vector(p);tangent=(Vector(points[min(j+1,len(points)-1)])-Vector(points[max(j-1,0)])).normalized()
        axis=tangent.cross(Vector((1,0,0)))
        if axis.length<.1:axis=tangent.cross(Vector((0,1,0)))
        axis.normalize();b=tangent.cross(axis).normalized();row=[]
        rr=radii[j];rx,ry=rr if isinstance(rr,tuple) else (rr,rr)
        for i in range(seg+1):
            a=2*math.pi*i/seg;v=p+axis*math.cos(a)*rx+b*math.sin(a)*ry
            row.append(addv(v,uvpanel(panel,j/(len(points)-1),i/seg),wws[j]))
        ids.append(row)
    for j in range(len(ids)-1):
        for i in range(seg):faces.extend([(ids[j][i],ids[j+1][i],ids[j+1][i+1]),(ids[j][i],ids[j+1][i+1],ids[j][i+1])])
    for end,rev in [(0,False),(-1,True)]:
        mid=addv(points[end],uvpanel(panel,float(end!=0),.5),wws[end])
        for i in range(seg):faces.append((mid,ids[end][i+1],ids[end][i]) if rev else (mid,ids[end][i],ids[end][i+1]))

# Continuous original torso: compact waist, deep feline chest, rounded haunches.
sections=[(.092,.193,.006,.012),(.078,.197,.029,.041),(.050,.198,.044,.052),(.015,.200,.046,.055),(-.025,.205,.043,.055),(-.065,.214,.039,.054),(-.105,.217,.043,.056),(-.138,.213,.041,.052),(-.165,.219,.029,.041),(-.190,.232,.023,.031)]
rows=[];seg=20
for j,(z,y,rx,ry) in enumerate(sections):
    row=[]
    for i in range(seg+1):
        t=2*math.pi*i/seg;p=(rx*math.sin(t),y+ry*math.cos(t),z)
        row.append(addv(p,uvpanel(0,j/(len(sections)-1),i/seg),blendz(z)))
    rows.append(row)
for j in range(len(rows)-1):
    for i in range(seg):faces.extend([(rows[j][i],rows[j][i+1],rows[j+1][i+1]),(rows[j][i],rows[j+1][i+1],rows[j+1][i])])
for j in (0,len(rows)-1):
    z,y,_,_=sections[j];mid=addv((0,y,z),uvpanel(0,j/(len(rows)-1),.5),blendz(z))
    for i in range(seg):faces.append((mid,rows[j][i+1],rows[j][i]) if j==0 else (mid,rows[j][i],rows[j][i+1]))

# Limbs follow bind-pose joints, with a muscular upper leg, slim distal leg and
# individual padded paws. Geometry is authored here; never sampled from vanilla.
for side in ['L','R']:
    sx=1 if side=='L' else -1
    for front in [True,False]:
        ns=[f'Bip01_{side}_'+s for s in (['Clavicle','UpperArm','Forearm','Hand','Finger0'] if front else ['Thigh','Calf','Foot','Toe0'])]
        pp=[bp(n) for n in ns]
        if front:
            pp[0]+=Vector((sx*.003,.009,0));rad=[.026,.023,.016,.012,.012]
        else:rad=[.033,.022,.014,.014]
        pts=[];rs=[];ws=[]
        for k in range(len(pp)-1):
            for t in [0,.5]:
                pts.append(pp[k].lerp(pp[k+1],t));rs.append(rad[k]*(1-t)+rad[k+1]*t);ws.append(mix(ns[k],ns[k+1],t))
        pts.append(pp[-1]);rs.append(rad[-1]);ws.append({ns[-1]:1})
        tube(pts,rs,ws,12,2)
        paw=pp[-2].lerp(pp[-1],.65)+Vector((0,.008,-.009))
        ellipsoid(paw,(.020,.014,.027),mix(ns[-2],ns[-1],.65),14,7,2)
        # Three subtle toe grooves are dark small tapered marks, part of atlas.
        for dx in [-.007,.007]:
            ellipsoid(paw+Vector((dx,.006,-.021)),(.0008,.003,.006),mix(ns[-2],ns[-1],.65),6,4,palette=1)

# Feline cranium, short paired muzzle, chin and triangular cartilage ears.
HEAD=bp('Bip01_Head')+Vector((0,.033,-.032))
hw={'Bip01_Head':1}
ellipsoid((0,.228,-.183),(.028,.032,.038),{'Bip01_Neck':.85,'Bip01_Head':.15},16,10,1)
ellipsoid(HEAD,(.048,.045,.044),hw,24,14,1)
ellipsoid(HEAD+Vector((0,-.026,-.013)),(.031,.020,.025),hw,16,8,palette=0)
for sx in [-1,1]:
    ellipsoid(HEAD+Vector((sx*.013,-.013,-.034)),(.018,.014,.017),hw,14,8,palette=0)
    # Three-dimensional almond eyes, green-gold iris, upright dark slit, glint.
    eye=HEAD+Vector((sx*.023,.009,-.035))
    ellipsoid(eye,(.013,.009,.005),hw,16,8,palette=3)
    ellipsoid(eye+Vector((0,0,-.002)),(.0105,.007,.0035),hw,16,8,palette=4)
    ellipsoid(eye+Vector((0,0,-.005)),(.002,.0065,.0012),hw,10,6,palette=5)
    ellipsoid(eye+Vector((-.002,.003,-.0058)),(.0015,.0015,.0008),hw,8,5,palette=6)
    # Ears are two-sided tapered triangular shells with a recessed inner face.
    ear=[HEAD+Vector((sx*x,y,z)) for x,y,z in [(.012,.025,.007),(.045,.018,.004),(.040,.067,.008),(.015,.023,-.015),(.046,.018,-.010),(.040,.067,.003)]]
    ids=[addv(p,uvpanel(1,.2+k*.08,.25),hw) for k,p in enumerate(ear)]
    for tri in [(0,1,2),(3,5,4),(0,3,4),(0,4,1),(1,4,5),(1,5,2),(2,5,3),(2,3,0)]:faces.append(tuple(ids[k] for k in tri))
    inner=[HEAD+Vector((sx*x,y,z)) for x,y,z in [(.020,.028,-.016),(.039,.026,-.013),(.039,.056,.000)]]
    ids=[addv(p,pal(2),hw) for p in inner];faces.append(tuple(ids))
    # Original thin whisker ribbons, ivory with opaque alpha for game shader.
    for j in range(3):
        a=HEAD+Vector((sx*.021,-.012+j*.004,-.045));b=a+Vector((sx*(.035+.004*j),-.007+j*.005,-.002))
        ids=[addv(p,pal(6),hw) for p in [a,b,b+Vector((0,.00055,0)),a+Vector((0,.00055,0))]]
        faces.extend([(ids[0],ids[1],ids[2]),(ids[0],ids[2],ids[3])])
# Nose is a small down-pointing pink wedge.
nose=HEAD+Vector((0,-.006,-.052));ids=[addv(nose+Vector(p),pal(2),hw) for p in [(-.007,.004,0),(.007,.004,0),(0,-.003,-.002),(0,.002,.004)]]
faces.extend([tuple(ids[i] for i in t) for t in [(0,2,1),(0,1,3),(1,2,3),(2,0,3)]])
ellipsoid(HEAD+Vector((0,-.019,-.047)),(.0008,.008,.0008),hw,6,4,palette=3)

# Thin, long tapered feline tail, weighted over all three native tail joints.
tailnodes=[bp('Bip01_Tail'),bp('Bip01_Tail1'),bp('Bip01_Tail2')]
tailnodes.append(tailnodes[-1]+(tailnodes[-1]-tailnodes[-2]).normalized()*.071)
tn=['Bip01_Tail','Bip01_Tail1','Bip01_Tail2','Bip01_Tail2'];pts=[];rs=[];ws=[]
for k in range(3):
    for t in [0,.25,.5,.75]:
        pts.append(tailnodes[k].lerp(tailnodes[k+1],t));rs.append(.014*(1-(k+t)/3)**.45+.002);ws.append(mix(tn[k],tn[k+1],t) if tn[k]!=tn[k+1] else {tn[k]:1})
pts.append(tailnodes[-1]);rs.append(.002);ws.append({'Bip01_Tail2':1});tube(pts,rs,ws,12,3)

mesh=bpy.data.meshes.new('Ewings_Cat_OriginalMesh');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('EwingsCat_Adult_BrownTabby',mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
uv=mesh.uv_layers.new(name='OriginalCoatUV')
for poly in mesh.polygons:
    poly.use_smooth=True
    for li in poly.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
# Ensure coherent outside normals on disconnected closed surfaces.
bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
for n in OFF:obj.vertex_groups.new(name=n)
for i,ww in enumerate(weights):
    for n,w in ww.items():obj.vertex_groups[n].add([i],w,'REPLACE')

# Build Blender's local rig only for authoring/offline deformation checks.
arm=bpy.data.armatures.new('Native_motion_compatibility');rig=bpy.data.objects.new('CompatibilityRig',arm);bpy.context.collection.objects.link(rig)
obj.select_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for n in FF:
    if n=='Raccoon':continue
    eb=arm.edit_bones.new(n);eb.length=.025;eb.matrix=C@BW[n]@Q
    par=FF[n]['parent']
    if par and par in arm.edit_bones:eb.parent=arm.edit_bones[par]
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
mod=obj.modifiers.new('Native skeletal deformation','ARMATURE');mod.object=rig;obj.parent=rig
obj['provenance']='Original geometry, coat, UV, facial details and weights generated by tools/build_cat.py. Native compatibility bone identifiers/bind alignment only.'

def fmt(v):return f'{float(v):.9f}'
def mattext(m):return ','.join(fmt(x) for row in m.transposed() for x in row)+';;'
def export_x(path):
    # Original mesh, original UV/normals, computed inverse bind transforms; NO
    # AnimationSet and NO proprietary native mesh/texture/animation payload.
    vv=[native(v.co) for v in mesh.vertices];nn=[native(v.normal) for v in mesh.vertices]
    tris=[tuple(p.vertices) for p in mesh.polygons];out=['xof 0303txt 0032','Frame EwingsCat {','FrameTransformMatrix { '+mattext(Matrix.Identity(4))+' }','Mesh EwingsCatMesh {',str(len(vv))+';']
    out += [';'.join(fmt(x) for x in v)+';'+(';' if i==len(vv)-1 else ',') for i,v in enumerate(vv)]
    out += [str(len(tris))+';']+['3;'+','.join(map(str,t))+';'+(';' if i==len(tris)-1 else ',') for i,t in enumerate(tris)]
    out += ['MeshNormals {',str(len(nn))+';']+[';'.join(fmt(x) for x in v)+';'+(';' if i==len(nn)-1 else ',') for i,v in enumerate(nn)]
    out += [str(len(tris))+';']+['3;'+','.join(map(str,t))+';'+(';' if i==len(tris)-1 else ',') for i,t in enumerate(tris)]+['}']
    out += ['MeshTextureCoords {',str(len(uvs))+';']+[fmt(u)+';'+fmt(1-v)+';'+(';' if i==len(uvs)-1 else ',') for i,(u,v) in enumerate(uvs)]+['}']
    out += ['MeshMaterialList { 1; '+str(len(tris))+'; '+','.join('0' for t in tris)+';; Material Coat { 1;1;1;1;; 0; 0;0;0;; 0;0;0;; TextureFilename { "EwingsCat_BrownTabby.png"; } } }']
    used=[n for n in OFF if any(n in w for w in weights)]
    out += [f'XSkinMeshHeader {{ {max(map(len,weights))}; {len(used)}; {len(used)}; }}']
    for n in used:
        entries=[(i,w[n]) for i,w in enumerate(weights) if n in w]
        out += ['SkinWeights { "'+n+'";',str(len(entries))+';',','.join(str(i) for i,w in entries)+';',','.join(fmt(w) for i,w in entries)+';',mattext(BW[n].inverted()),'}']
    out += ['}','}']
    def writebone(n):
        par=FF[n]['parent'];local=BW[par].inverted()@BW[n] if par in BW else BW[n]
        out.extend(['Frame '+n+' {','FrameTransformMatrix { '+mattext(local)+' }'])
        for child,f in FF.items():
            if child in BW and f['parent']==n:writebone(child)
        out.append('}')
    for n,f in FF.items():
        if n in BW and f['parent'] is None:writebone(n)
    path.write_text('\n'.join(out)+'\n',encoding='utf-8')
export_x(ASSETS/'models_X/Skinned/EwingsCat_Adult.x')

# Compare native quaternion conventions against source frame matrices. The .x
# rotation keys use conjugate quaternions relative to column-vector matrices.
def sample(rows,t,quaternion=False):
    if len(rows)==1:return rows[0][1]
    before=max((r for r in rows if r[0]<=t),default=rows[0],key=lambda r:r[0]);after=min((r for r in rows if r[0]>=t),default=rows[-1],key=lambda r:r[0])
    f=(t-before[0])/(after[0]-before[0]) if after[0]!=before[0] else 0
    if quaternion:
        return Quaternion(before[1]).slerp(Quaternion(after[1]),f)
    return Vector(before[1]).lerp(Vector(after[1]),f)

def apply_native_pose(path,fraction):
    tracks,ticks=animation(path);duration=max(t for tr in tracks.values() for rows in tr.values() for t,v in rows);t=duration*fraction
    # Determine convention from embedded walk frame at zero, once.
    if not hasattr(apply_native_pose,'conjugate'):
        reftracks,_=animation(REF);errors=[]
        for conj in [False,True]:
            err=0
            for n,tr in reftracks.items():
                if n in FF and 0 in tr:
                    q=Quaternion(tr[0][0][1]);q=q.conjugated() if conj else q
                    err+=sum(abs(q.to_matrix()[i][j]-FF[n]['local'][i,j]) for i in range(3) for j in range(3))
            errors.append(err)
        apply_native_pose.conjugate=errors[1]<errors[0];print('QUATERNION_CONVENTION',errors,apply_native_pose.conjugate)
    aw={}
    for n,f in FF.items():
        if n not in BW:continue
        tr=tracks.get(n);local=Matrix(f['local'].tolist())
        if tr:
            trans=sample(tr[2],t) if 2 in tr else local.translation
            rot=sample(tr[0],t,True) if 0 in tr else local.to_quaternion()
            if 0 in tr and apply_native_pose.conjugate:rot=rot.conjugated()
            scale=sample(tr[1],t) if 1 in tr else Vector((1,1,1))
            local=Matrix.LocRotScale(trans,rot,scale)
        par=f['parent'];aw[n]=aw[par]@local if par in aw else local
        # Convert desired local matrices to Blender bone-space basis exactly.
        rest=rig.data.bones[n].matrix_local
        if par in aw:
            desired=(C@aw[par]@Q).inverted()@(C@aw[n]@Q)
            restlocal=rig.data.bones[par].matrix_local.inverted()@rest
        else:desired=C@aw[n]@Q;restlocal=rest
        rig.pose.bones[n].matrix_basis=restlocal.inverted()@desired
    bpy.context.view_layer.update()
    apply_native_pose.last_aw = aw
    dg=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dg);me=ev.to_mesh();arr=np.array([tuple(v.co) for v in me.vertices]);ev.to_mesh_clear()
    assert np.isfinite(arr).all()
    return {'clip':path.name,'fraction':fraction,'bounds':[[float(x) for x in arr.min(0)],[float(x) for x in arr.max(0)]]}

scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_x=720;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.world.color=(.06,.06,.06);scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,location,energy,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=location;aim(o,(0,0,.15))
light('Warm softbox',(.6,.8,1),12,.7);light('Cool fill',(-.6,.4,.5),6,.6);light('Rim',(.15,-.7,.7),10,.5)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006));ground=bpy.context.object;ground.name='Preview ground';gm=bpy.data.materials.new('Warm grey stage');gm.diffuse_color=(.11,.12,.13,1);ground.data.materials.append(gm)
cd=bpy.data.cameras.new('PreviewCamera');cam=bpy.data.objects.new('PreviewCamera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.ortho_scale=.64;cd.lens=70
def render(name,location,target=(0,.035,.16),scale=.64):
    cam.location=location;aim(cam,target);cd.ortho_scale=scale;scene.render.filepath=str(ROOT/'previews'/name);bpy.ops.render.render(write_still=True)

# Keep .blend in original bind pose, without embedded native animation actions.
rig.pose.bones.foreach_set if False else None
for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update();img.pack();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/EwingsCat_Adult.blend'))
if '--no-render' in sys.argv:
    print('ORIGINAL_MESH_BUILT_NO_RENDER',len(verts),len(faces));sys.exit(0)
render('01_three_quarter.png',(.64,.78,.42))
render('02_side.png',(.8,.02,.27))
render('03_front.png',(0,.9,.32),target=(0,.08,.19),scale=.48)
poses=[]
for name,clip,fraction in [('04_idle_pose.png','Rac_Idle01.x',.4),('05_walk_pose.png','Rac_Walk.x',.35),('06_run_pose.png','Rac_Run.x',.3),('07_lying_pose.png','Rac_IdleLyingDown.x',.5)]:
    p=GAME/'media/anims_X/Raccoon'/clip;poses.append(apply_native_pose(p,fraction));render(name,(.64,.78,.42))

# Original transparent icon made from this model, not native inventory artwork.
for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update();ground.hide_render=True;scene.render.film_transparent=True;scene.render.resolution_x=128;scene.render.resolution_y=128
cam.location=(.64,.78,.42);aim(cam,(0,.04,.17));cd.ortho_scale=.57;scene.render.filepath=str(ASSETS/'textures/Item_EwingsCat_Adult.png');bpy.ops.render.render(write_still=True)

# A contact sheet is an offline Blender preview, never an in-game screenshot.
files=sorted((ROOT/'previews').glob('0*.png'));tw,th=450,400;sheet=np.ones((th*2,tw*4,4),dtype=np.float32);sheet[:,:,:3]=.075
for i,p in enumerate(files):
    im=bpy.data.images.load(str(p),check_existing=False);im.scale(tw,th);ar=np.array(im.pixels[:],dtype=np.float32).reshape(th,tw,4);row=1-i//4;col=i%4;sheet[row*th:(row+1)*th,col*tw:(col+1)*tw]=ar;bpy.data.images.remove(im)
out=bpy.data.images.new('Offline Blender preview sheet',width=tw*4,height=th*2,alpha=True);out.pixels.foreach_set(sheet.ravel());out.file_format='PNG';out.filepath_raw=str(ROOT/'previews/EwingsAnimals_cat_preview.png');out.save()
report={'vertices':len(verts),'triangles':len(faces),'weighted_bones':sorted(set(n for w in weights for n in w)),'max_influences':max(map(len,weights)),'max_weight_sum_error':max(abs(sum(w.values())-1) for w in weights),'native_reference_sha256':sha(REF),'original_geometry':True,'native_animation_payload_exported':False,'poses':poses,'quaternion_conjugate':bool(apply_native_pose.conjugate),'scope':'Offline Blender deformation only; game import and gameplay not certified.'}
(ROOT/'verification/art_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('EWINGS_BUILD',json.dumps(report))
