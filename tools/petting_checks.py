"""B42.21 petting parser, native action delegation and asset-preservation checks.

Executes native Lua in an isolated VM with stubs, never a world or saved animal.
Native Lua used by the fixture is read locally and is not packaged as source.
"""
from pathlib import Path
import hashlib,json,re,struct,subprocess,zipfile,xml.etree.ElementTree as ET
from inspect_native import GAME,sha
ROOT=Path(__file__).resolve().parents[1];MEDIA=ROOT/'stage/EwingsAnimals/42/media';OUT=ROOT/'verification'
PRIVATE=ROOT/'release/petting-checks';PRIVATE.mkdir(parents=True,exist_ok=True)
JAVA=GAME/'jre64/bin/java.exe';CP=str(OUT/'probes')+';'+str(GAME/'projectzomboid.jar')
def run(cls,path):
    r=subprocess.run([str(JAVA),'-cp',CP,cls,str(path)],capture_output=True,text=True,cwd=str(GAME),timeout=45)
    assert r.returncode==0,(cls,r.stdout,r.stderr)
    return {'exit_code':r.returncode,'stdout':r.stdout.strip(),'stderr':r.stderr.strip()}

def native_method_refs(class_name,method_name):
    b=zipfile.ZipFile(GAME/'projectzomboid.jar').read(class_name);p=8
    def rd(fmt):
        nonlocal p
        n=struct.calcsize(fmt);v=struct.unpack_from(fmt,b,p);p+=n;return v[0] if len(v)==1 else v
    count=rd('>H');cp=[None]*count;i=1
    while i<count:
        t=rd('>B')
        if t==1:n=rd('>H');cp[i]=(t,b[p:p+n].decode('utf8',errors='replace'));p+=n
        elif t in (3,4):cp[i]=(t,rd('>i' if t==3 else '>f'))
        elif t in (5,6):p+=8;i+=1
        elif t in (7,8,16,19,20):cp[i]=(t,rd('>H'))
        elif t in (9,10,11,12,17,18):cp[i]=(t,rd('>H'),rd('>H'))
        elif t==15:cp[i]=(t,rd('>B'),rd('>H'))
        else:raise AssertionError(('Unknown constant pool tag',t))
        i+=1
    def resolve(i):
        v=cp[i]
        if not v:return '#'+str(i)
        if v[0] in (1,3,4):return str(v[1])
        if v[0] in (7,8):return resolve(v[1])
        if v[0] in (9,10,11,12):return resolve(v[1])+'.'+resolve(v[2])
        return '#'+str(i)
    p+=6;ni=rd('>H');p+=2*ni
    for _ in range(rd('>H')):
        p+=6
        for a in range(rd('>H')):rd('>H');n=rd('>I');p+=n
    code=None
    for _ in range(rd('>H')):
        rd('>H');name=resolve(rd('>H'));rd('>H')
        for a in range(rd('>H')):
            an=resolve(rd('>H'));n=rd('>I');end=p+n
            if name==method_name and an=='Code':p+=4;size=rd('>I');code=b[p:p+size]
            p=end
    assert code is not None,method_name
    q=0;refs=[]
    while q<len(code):
        op=code[q];q+=1;step=0
        if op==18:step=1
        elif op in (19,20,178,179,180,181,182,183,184,185,186,187,189,192,193,197):
            step=4 if op in (185,186) else 3 if op==197 else 2
            if op in (178,179,180,181,182,183,184,185):refs.append(resolve(struct.unpack_from('>H',code,q)[0]))
        elif op in (16,21,22,23,24,25,54,55,56,57,58,169,188):step=1
        elif op in (17,132,198,199) or 153<=op<=168:step=2
        elif op in (200,201):step=4
        elif op==196:step=5 if code[q]==132 else 3
        elif op in (170,171):raise AssertionError('Native petting method changed: inspect switch')
        q+=step
    return sorted(set(refs)),hashlib.sha256(code).hexdigest()

native_paths=['media/lua/shared/TimedActions/Animals/ISPetAnimal.lua','media/lua/client/ISUI/Animal/ISAnimalContextMenu.lua','media/AnimSets/player/petanimal/defaultpet.xml','media/AnimSets/player/petanimal/petraccoonboar.xml']
native_paths.append('media/lua/shared/TimedActions/Animals/ISPickupAnimal.lua')
before={p:sha(GAME/p) for p in native_paths}
nodepath=MEDIA/'AnimSets/player/petanimal/petewingsanimalscatadult.xml';node=ET.parse(nodepath).getroot()
conditions=node.findall('m_Conditions');assert len(conditions)==1
assert conditions[0].findtext('m_Name')=='animal' and conditions[0].findtext('m_Type')=='STRING'
assert conditions[0].findtext('m_Value')=='ewingsanimals_catadult'
assert node.findtext('m_Looped')=='false'
assert node.findtext('m_Scalar')=='AnimalSizeX' and node.findtext('m_Scalar2')=='AnimalSizeY'
clips=[x.findtext('m_AnimName') for x in node.findall('m_2DBlends')]
native_node=ET.parse(GAME/'media/AnimSets/player/petanimal/petraccoonboar.xml').getroot()
assert clips==[x.findtext('m_AnimName') for x in native_node.findall('m_2DBlends')]
assert node.findtext('m_AnimName')==native_node.findtext('m_AnimName')
for clip in clips:assert (GAME/'media/anims_X/Bob'/f'{clip}.x').is_file()
ids={x.attrib['referenceID'] for x in node.findall('m_2DBlends')};assert ids=={'1','2','3'}
assert {x.text for x in node.find('m_2DBlendTri')}==ids
events=node.findall('m_Events');assert len(events)==1 and events[0].findtext('m_EventName')=='pettingFinished' and events[0].findtext('m_Time')=='End'
xml_result=run('NativeAnimNodeProbe',nodepath);assert 'ANIM_NODE_PARSE_OK' in xml_result['stdout']
translations=json.loads((MEDIA/'lua/shared/Translate/EN/IG_UI.json').read_text(encoding='utf-8'))
assert translations['IGUI_Animal_Group_ewingsanimals_cat']=='Cats'
assert json.loads((GAME/'media/lua/shared/Translate/EN/ContextMenu.json').read_text(encoding='utf-8'))['ContextMenu_PetAnimal']=='Pet'
context=(GAME/native_paths[1]).read_text(encoding='utf-8')
assert 'if animal:canBePet() then' in context and 'ISTimedActionQueue.add(ISPetAnimal:new(chr, animal))' in context
assert 'animal:getAttachmentWorldPos("head")' in context
refs,methodsha=native_method_refs('zombie/characters/animals/IsoAnimal.class','petAnimal')
assert any('.changeStress.' in r for r in refs) and any('.petTimer.' in r for r in refs)
assert any('.getAcceptanceLevel.' in r for r in refs) and any('.getPerkLevel.' in r for r in refs)

definition=(MEDIA/'lua/shared/Definitions/animal/EwingsAnimals_CatDefinitions.lua').read_text(encoding='utf-8')
fixture=definition+'''
require=function() end
ISBaseTimedAction={}
function ISBaseTimedAction:derive(name) return {} end
function ISBaseTimedAction.stop(self) end
function ISBaseTimedAction.perform(self) end
isClient=function() return false end
isServer=function() return false end
forceDropHeavyItems=function(c) end
'''+(GAME/native_paths[0]).read_text(encoding='utf-8')+'''
local def=AnimalDefinitions.animals.ewingsanimals_catadult
assert(def.canBePet and def.alwaysFleeHumans and def.wild)
assert(not def.male and not def.female and def.mate==nil)
assert(def.babyType=="ewingsanimals_kitten" and def.stages.ewingsanimals_catadult.nextStage==nil)
local fields={}; local blocked=false; local distance=2.99; local dwarf=false
local calls=0; local stopped=0; local faced=0
local char={}
function char:setVariable(k,v) fields[k]=v end
function char:setIsAiming(v) assert(v==false) end
function char:faceThisObject(o) faced=faced+1 end
function char:shouldBeTurning() return false end
function char:getSquare() return {DistTo=function(s,o) return distance end} end
local animal={}
function animal:getSquare() return {} end
function animal:getData() return {getMaxSize=function() return def.maxSize end,getMinSize=function() return def.minSize end,getSize=function() return 1 end} end
function animal:getBehavior() return {setBlockMovement=function(self,v) blocked=v end} end
function animal:getAnimalType() return "ewingsanimals_catadult" end
function animal:hasGeneticDisorder(s) assert(s=="dwarf");return dwarf end
function animal:isBaby() return false end
function animal:getBabyType() return def.babyType end
function animal:setVariable(k,v) fields["animal_"..k]=v end
function animal:clearVariable(k) fields["animal_"..k]=nil end
function animal:faceThisObject(o) assert(o==char) end
function animal:petAnimal(c) assert(c==char);calls=calls+1 end
local action=setmetatable({character=char,animal=animal,netAction={},action={forceStop=function() stopped=stopped+1 end}},{__index=ISPetAnimal})
function action:setOverrideHandModels(a,b) assert(a==nil and b==nil) end
assert(action:isValid());distance=3;assert(not action:isValid());distance=2.99
assert(action:waitToStart()==false);action:update()
for _,isDwarf in ipairs({false,true}) do
    dwarf=isDwarf;action:start()
    assert(fields.animal==(isDwarf and "ewingsanimals_kitten" or "ewingsanimals_catadult") and fields.petanimal==true)
    assert(math.abs(fields.AnimalSizeY-0.5)<0.00001 and fields.AnimalSizeX==0.01)
    assert(blocked and fields.animal_idleAction=="petting")
    action:stop();assert(not blocked and not fields.petanimal and fields.animal_idleAction==nil)
end
assert(action:complete()==true and calls==1)
action:animEvent("unrelated",nil);assert(calls==1)
action:start();action:animEvent("pettingFinished",nil)
assert(calls==2 and stopped==1 and not blocked and not fields.petanimal)
action:start();action:perform();assert(not blocked and not fields.petanimal)
local emulated=false
emulateAnimEventOnce=function(net,delay,event,param) assert(net==action.netAction and delay==3000 and event=="pettingFinished");emulated=true end
action:serverStart();assert(emulated)
'''
fp=PRIVATE/'native_action_assertions.lua';fp.write_text(fixture,encoding='utf-8',newline='\n');lua_result=run('NativeLuaExec',fp)

pickup_refs,pickup_methodsha=native_method_refs('zombie/characters/animals/IsoAnimal.class','canBePicked')
assert any('.canBePicked.' in r for r in pickup_refs) and any('.getWeight.' in r for r in pickup_refs)
assert any('.Strength.' in r for r in pickup_refs) and any('.getPerkLevel.' in r for r in pickup_refs)
assert not any('acceptance' in r.lower() or '.isWild.' in r for r in pickup_refs)
assert 'if animal:canBePicked(playerObj) then' in context
pickup_callback=re.search(r'AnimalContextMenu\.onPickupAnimal = function\(animal, chr\).*?\nend',context,re.S).group(0)
pickup_fixture=fixture+'\n'+(GAME/native_paths[-1]).read_text(encoding='utf-8')+'''
local exists=true;local wild=true;local removedWorld=false;local removedSquare=false
local attachedCleared=false;local inventoryAdded=nil;local primary=nil;local secondary=nil;local instant=false
function animal:isExistInTheWorld() return exists end
function animal:setWild(v) wild=v end
function animal:removeFromWorld() removedWorld=true;exists=false end
function animal:removeFromSquare() removedSquare=true end
function animal:setSquare(v) assert(v==nil) end
function animal:playBreedSound(n) assert(n=="pick_up");return 0 end
function animal:stopAllMovementNow() end
local oldGetData=animal.getData
function animal:getData() local d=oldGetData(self);d.setAttachedPlayer=function(self,p) assert(p==nil);attachedCleared=true end;return d end
function char:SetVariable(k,v) fields[k]=v end
function char:reportEvent(n) assert(n=="EventLootItem") end
function char:stopOrTriggerSound(s) end
function char:isTimedActionInstant() return instant end
function char:getInventory() return {AddItem=function(self,item) inventoryAdded=item end} end
function char:getAttachedAnimals() return {remove=function(self,a) assert(a==animal) end} end
function char:setPrimaryHandItem(v) primary=v end
function char:setSecondaryHandItem(v) secondary=v end
local item={setAnimal=function(self,a) assert(a==animal);self.animal=a end}
instanceItem=function(n) assert(n=="Base.Animal");return item end
local sent=false
sendPickupAnimal=function(a,c,i) assert(a==animal and c==char and i==item);sent=true end
local pickup=setmetatable({character=char,animal=animal},{__index=ISPickupAnimal})
function pickup:setActionAnim(n) assert(n=="Loot") end
distance=2.99;assert(pickup:isValid());distance=3;assert(not pickup:isValid())
distance=2.99;exists=false;assert(not pickup:isValid());exists=true
assert(pickup:getDuration()==30);instant=true;assert(pickup:getDuration()==1);instant=false
pickup:start();assert(blocked and fields.LootPosition=="Low")
pickup:stop();assert(not blocked);pickup:start();pickup:perform();assert(not blocked)
function ISBaseTimedAction.new(cls,c) return setmetatable({character=c},{__index=cls}) end
local adjacent=false;local queued=nil
luautils={walkAdj=function(c,s) assert(c==char);return adjacent end}
ISTimedActionQueue={add=function(action) queued=action end}
AnimalContextMenu={}
'''+pickup_callback+'''
AnimalContextMenu.onPickupAnimal(animal,char);assert(queued==nil)
adjacent=true;AnimalContextMenu.onPickupAnimal(animal,char)
assert(queued and queued.animal==animal and queued.character==char)
distance=3;assert(pickup:complete()==false and inventoryAdded==nil and wild)
distance=2.99;assert(pickup:complete()==true)
assert(inventoryAdded==item and item.animal==animal and primary==item and secondary==item)
assert(not wild and removedWorld and removedSquare and attachedCleared and sent)
assert(pickup:complete()==false)
'''
pp=PRIVATE/'native_pickup_assertions.lua';pp.write_text(pickup_fixture,encoding='utf-8',newline='\n');pickup_result=run('NativeLuaExec',pp)
for path in MEDIA.rglob('*.lua'):
    text=path.read_text(encoding='utf-8');assert 'changeStress(' not in text and 'ISPetAnimal =' not in text and 'AnimalContextMenu.onPickupAnimal =' not in text and 'AnimalContextMenu.doMenu =' not in text

# Verify all original runtime art and the authoring source against the published
# v0.1.0 archives; the petting update requires no mesh/texture/rig changes.
installzip=zipfile.ZipFile(ROOT/'release/remote-v0.1.0/EwingsAnimals-0.1.0-prototype-install.zip')
sourcezip=zipfile.ZipFile(ROOT/'release/remote-v0.1.0/EwingsAnimals-0.1.0-prototype-source.zip')
assets={}
for rel in ['models_X/Skinned/EwingsCat_Adult.x','textures/Body/EwingsCat_BrownTabby.png','textures/Item_EwingsCat_Adult.png']:
    current=(MEDIA/rel).read_bytes();assert current==installzip.read('EwingsAnimals/42/media/'+rel);assets[rel]=hashlib.sha256(current).hexdigest()
blend=(ROOT/'art/EwingsCat_Adult.blend').read_bytes();assert blend==sourcezip.read('EwingsAnimals/art/EwingsCat_Adult.blend');assets['art/EwingsCat_Adult.blend']=hashlib.sha256(blend).hexdigest()
assert all(sha(GAME/p)==h for p,h in before.items())
report={'version':'0.1.2','all_passed':True,'group_translation':'Cats','native_xml_parser':xml_result,'native_action_stub_execution':lua_result,'native_pickup_stub_execution':pickup_result,'native_pickup_gate':'canBePicked and weight < 40 + 7 * Strength (or native god/unlimited-carry exception); no acceptance threshold','native_pickup_gate_method_sha256':pickup_methodsha,'native_pickup_gate_references':pickup_refs,'pickup_override_added':False,'reported_live_pickup_issue_reproduced':False,'native_pet_method_bytecode_sha256':methodsha,'native_pet_method_references':refs,'native_low_pet_clips':clips,'normal_and_dwarf_adult_selection':True,'native_distance_boundary_and_action_cleanup':True,'native_effect_delegation':True,'custom_stress_values':False,'global_overrides':False,'unchanged_original_asset_sha256':assets,'native_reference_hashes':before,'limits':['Lua action assertions use stubs, not a saved animal or game world.','Stress/cooldown effects are delegated to the inspected native engine method, not reimplemented or gameplay-tested.','The reported live pickup failure was not reproduced; distinguish a missing menu option, failed path/action or a fleeing animal before changing behavior.','Live hand/head alignment, existing-cat reload and multiplayer require runtime acceptance.','Installed files are not updated by this checker.']}
(OUT/'petting_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('PETTING_CHECKS_OK',json.dumps({'xml':xml_result['exit_code'],'action':lua_result['exit_code'],'unchanged_assets':len(assets)}))
