"""Offline checks only. Runs installed parsers, never launches the game."""
from pathlib import Path
import sys,json,re,subprocess,hashlib,numpy as np
from inspect_native import GAME,frames,skin_offsets,sha,NUMBER
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'stage/EwingsAnimals';MEDIA=MOD/'42/media';OUT=ROOT/'verification';OUT.mkdir(exist_ok=True)
JAVA=GAME/'jre64/bin/java.exe';CP=str(OUT/'probes')+';'+str(GAME/'projectzomboid.jar')
results={}
def run(name,cls,path):
    p=subprocess.run([str(JAVA),'--enable-native-access=ALL-UNNAMED','-cp',CP,cls,str(path)],capture_output=True,text=True,timeout=45,cwd=str(GAME))
    results[name]={'exit_code':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}
    if p.returncode:raise AssertionError(name+': '+p.stdout+p.stderr)
    return p.stdout

baseline={
 'media/lua/shared/Definitions/animal/RaccoonDefinitions.lua':'55185497017826ae3a1d3f3e980f963de29644797ea4d992d40ea9e483ca502c',
 'media/scripts/generated/models_animals.txt':'148a08e544ea44714617681bac2d770ad82beac899a20e3b51ec40c72950a1d0',
 'media/models_X/Skinned/Raccoon_Body.x':'a8cc66ee09bae74f02f1dbc045a528989cb02e9f7df5ec720f25b8d706348320',
 'projectzomboid.jar':'e1a69eb743ede60b213a0fe7f8b83d4fcab773036d256cc4543a336f3b058a33',
}
native_hashes={k:{'before':v,'after':sha(GAME/k)} for k,v in baseline.items()}
assert all(h['before']==h['after'] for h in native_hashes.values()),'A native reference changed'
(OUT/'native_reference_hashes.json').write_text(json.dumps(native_hashes,indent=2)+'\n')

meshpath=MEDIA/'models_X/Skinned/EwingsCat_Adult.x';text=meshpath.read_text()
assert 'AnimationSet' not in text
head=re.search(r'Mesh EwingsCatMesh\s*\{(.*?)MeshNormals',text,re.S)[1];nums=re.findall(NUMBER,head);nv=int(nums[0]);p=1+3*nv;nf=int(nums[p]);p+=1
vv=np.array([float(x) for x in nums[1:1+3*nv]]).reshape(-1,3);ff=[]
for _ in range(nf):
    n=int(nums[p]);assert n==3;p+=1;ff.append([int(x) for x in nums[p:p+3]]);p+=3
ff=np.array(ff);assert ff.min()>=0 and ff.max()<nv
area=np.linalg.norm(np.cross(vv[ff[:,1]]-vv[ff[:,0]],vv[ff[:,2]]-vv[ff[:,0]]),axis=1)/2
assert np.isfinite(vv).all() and (area>1e-14).all(), 'Degenerate/nonfinite geometry'
weights=np.zeros(nv);influences=np.zeros(nv);nativeoff=skin_offsets(GAME/'media/models_X/Skinned/Raccoon_Body.x');ownoff=skin_offsets(meshpath);ownframes=frames(meshpath)
for m in re.finditer(r'SkinWeights\s*\{\s*"([^"]+)"\s*;([^}]+)',text):
    n=m[1];vals=re.findall(NUMBER,m[2]);count=int(vals[0]);ids=np.array([int(x) for x in vals[1:1+count]]);ww=np.array([float(x) for x in vals[1+count:1+2*count]])
    assert np.isfinite(ww).all() and (ww>0).all() and (ww<=1).all();weights[ids]+=ww;influences[ids]+=1
    assert n in nativeoff
    assert np.max(np.abs(ownoff[n]-nativeoff[n]))<2e-6
    assert np.max(np.abs(ownframes[n]['global']@ownoff[n]-np.eye(4)))<3e-6
assert np.max(np.abs(weights-1))<2e-8
assert influences.min()>=1 and influences.max()<=4
results['geometry']={'source_vertices':nv,'triangles':nf,'weighted_bones':len(ownoff),'max_influences':int(influences.max()),'max_weight_sum_error':float(np.max(np.abs(weights-1))),'minimum_triangle_area':float(area.min()),'native_animation_payloads':0}
run('native_mesh_import','NativeMeshProbe',meshpath)
for path in sorted(MEDIA.rglob('*.lua')):run('lua_compile_'+path.name,'NativeLuaProbe',path)
for path in sorted((MEDIA/'scripts').glob('*.txt')):run('native_script_parse_'+path.name,'NativeScriptProbe',path)
for path in (MEDIA/'lua/shared/Translate').rglob('*.json'):json.loads(path.read_text())

# Execute mod-owned definitions inside the installed Kahlua VM with a small
# isolated environment. No game classes/world/save loading are used.
defpath=MEDIA/'lua/shared/Definitions/animal/EwingsAnimals_CatDefinitions.lua'
avpath=MEDIA/'lua/shared/Definitions/animal/EwingsAnimals_Avatar.lua'
harness='AnimalDefinitions={animals={nativeSentinel={unchanged=true}}}; IsoDirections={SE=0,SW=1}\n'+defpath.read_text()+'\n'+avpath.read_text()+'''
local a=AnimalDefinitions.animals.ewingsanimals_catadult
assert(AnimalDefinitions.animals.nativeSentinel.unchanged)
local count=0;for k,v in pairs(AnimalDefinitions.animals) do count=count+1 end
assert(count==3 and a.bodyModel=="EwingsAnimals_CatAdult")
assert(a.group=="ewingsanimals_cat" and a.animset=="raccoon")
assert(a.stages.ewingsanimals_catadult.nextStage==nil)
assert(a.mate==nil and a.babyType=="ewingsanimals_kitten" and not a.male and not a.female)
assert(a.canBePet)
assert(a.eatTypeTrough=="CatFood,Meat,Fish,Base.CatFoodBag")
assert(a.feedByHandType=="CatFood,Meat,Fish,Base.CatFoodBag,CowMilk,AnimalMilk")
assert(a.breeds.ewingsanimals_browntabby.milkType=="CowMilk")
assert(a.canBePicked and a.alwaysFleeHumans and a.wild and a.canClimbStairs)
assert(a.stages.ewingsanimals_catadult.ageToGrow==60)
assert(not a.eatGrass and not a.canBeMilked and not a.udder)
assert(not a.attackBack and not a.attackIfStressed and a.baseDmg==0)
assert(a.dung==nil and a.dungChancePerDay==0)
assert(a.bodyModelSkel==nil and a.textureSkeleton==nil)
assert(AnimalAvatarDefinition.ewingsanimals_catadult.avatarWidth==200)
local k=AnimalDefinitions.animals.ewingsanimals_kitten
assert(k and k.stages.ewingsanimals_kitten.nextStage=="ewingsanimals_catadult")
assert(k.stages.ewingsanimals_kitten.nextStageMale=="ewingsanimals_catadult")
assert(k.stages.ewingsanimals_kitten.ageToGrow==60 and k.minAge==0)
assert(k.canBePicked and k.canBePet and not k.canBeAttached and not a.canBeAttached)
assert(not k.wild and not k.alwaysFleeHumans and k.minSize==0.5 and k.maxSize==0.9)
assert(k.mate==nil and k.minBaby==0 and k.maxBaby==0)
assert(k.bodyModel==a.bodyModel and k.breeds==a.breeds)
'''
hp=OUT/'definition_assertions.lua';hp.write_text(harness);run('native_lua_definition_execution','NativeLuaExec',hp)
assert 'id=EwingsAnimals' in (MOD/'42/mod.info').read_text()
assert (MOD/'common/README.txt').is_file()
assert (MEDIA/'textures/Body/EwingsCat_BrownTabby.png').is_file()
assert (MEDIA/'textures/Item_EwingsCat_Adult.png').is_file()
for path in MEDIA.rglob('*.lua'):
    t=path.read_text()
    assert not re.search(r'Events\.|OnTick|OnCreatePlayer|addAnimal\(|MigrationGroupDefinitions|TrapAnimals',t.replace('Events.OnFillWorldObjectContextMenu.Add(fill)','')),'Unrequested automatic spawn/event hook'
results['scope']={'new_species_only':True,'automatic_spawns':False,'companion_systems':False,'native_references_unchanged':True,'installation_performed':False,'game_launched':False,'runtime_certified':False,'multiplayer_certified':False}
version=re.search(r'(?m)^version=(.+)$',(MOD/'42/mod.info').read_text()).group(1).strip()
report={'version':version,'target':'B42.21 / Steam25485521','checks':results,'limits':['Assimp importer and script/Lua parsers are isolated asset checks, not game rendering.','No gameplay, save/reload or multiplayer tests were run by these checks.','Milk configuration and native consumption path are statically grounded; actual feeding needs disposable-world acceptance.']}
(OUT/'offline_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
