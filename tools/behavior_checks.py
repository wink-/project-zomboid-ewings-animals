"""Focused isolated B42.21 cat behavior/menu checks; never starts the game."""
from pathlib import Path
import json,subprocess,re,struct,zipfile,xml.etree.ElementTree as ET
from inspect_native import GAME,sha
from native_probes import Emitter
R=Path(__file__).resolve().parents[1]; M=R/'stage/EwingsAnimals/42/media'; O=R/'verification'; P=R/'release/behavior-checks';P.mkdir(parents=True,exist_ok=True)
java=GAME/'jre64/bin/java.exe';cp=str(O/'probes')+';'+str(GAME/'projectzomboid.jar')
def run(cls,p):
 r=subprocess.run([str(java),'-cp',cp,cls,str(p)],capture_output=True,text=True,cwd=GAME,timeout=45)
 assert r.returncode==0,(cls,r.stdout,r.stderr)
 return {'exit_code':r.returncode,'stdout':r.stdout.strip(),'stderr':r.stderr.strip()}

# Actual Java definition loader, not just successful Lua compilation. Give it an
# isolated Lua environment and locally read vanilla genome/raccoon definitions.
e=Emitter('NativeAnimalDefinitionProbe')
base=(R/'tools/native_probes.py').read_text().split("e=Emitter('NativeLuaExec')")[1].split("c+=e.label('LUA_EXECUTION_OK')")[0]
scope={'e':e};exec(base,globals(),scope);c=scope['c']
c+=b'\x2b'+e.ins(179,e.field('zombie/Lua/LuaManager','env','Lse/krka/kahlua/vm/KahluaTable;'))
c+=e.call('zombie/characters/animals/AnimalDefinitions','loadAnimalDefinitions','()V')
for kind in ['raccoonsow','raccoonboar','raccoonkit','ewingsanimals_catadult','ewingsanimals_kitten']:
 c+=e.label(kind)+e.ins(19,e.string(kind))+e.call('zombie/characters/animals/AnimalDefinitions','getDef','(Ljava/lang/String;)Lzombie/characters/animals/AnimalDefinitions;')+b'\x4e'
 for field,typ in [('canBePicked','Z'),('canBeAttached','Z'),('wild','Z'),('alwaysFleeHumans','Z'),('minWeight','F'),('maxWeight','F')]:
  c+=e.label(field)+e.out()+b'\x2d'+e.ins(180,e.field('zombie/characters/animals/AnimalDefinitions',field,typ))+e.call('java/io/PrintStream','println','('+typ+')V',182)
c+=e.label('ANIMAL_DEFINITIONS_PARSE_OK')+b'\xb1';e.write(c)
nativegenome=GAME/'media/lua/shared/Definitions/animal/AnimalGenomeDefinitions.lua'
nativerac=GAME/'media/lua/shared/Definitions/animal/RaccoonDefinitions.lua'
fixture='AnimalDefinitions={animals={}}\nfunction copyTable(t) local n={} for k,v in pairs(t) do if type(v)=="table" then n[k]=copyTable(v) else n[k]=v end end return n end\n'+nativegenome.read_text()+nativerac.read_text()+(M/'lua/shared/Definitions/animal/EwingsAnimals_CatDefinitions.lua').read_text()
p=P/'native_definitions.lua';p.write_text(fixture,encoding='utf-8');native=run('NativeAnimalDefinitionProbe',p)
assert 'ANIMAL_DEFINITIONS_PARSE_OK' in native['stdout']
for kind in ['ewingsanimals_catadult','ewingsanimals_kitten']:
 block=native['stdout'].split(kind+'\n')[1].split('maxWeight')[0]
 assert 'canBePicked\ntrue' in block and 'canBeAttached\nfalse' in block
 state='true' if kind=='ewingsanimals_catadult' else 'false'
 assert 'wild\n'+state in block and 'alwaysFleeHumans\n'+state in block

# Reproduce the inspected initWeight float calculation in the installed JVM.
# Actual initWeight also applies a gene factor to duration; zero stays zero.
e=Emitter('NativeWeightMathProbe');c=b''
def fl(v):return e.ins(19,e.cp(('float',v),b'\x04'+struct.pack('>f',v)))
for duration in [0,60]:
 c+=e.label('duration='+str(duration))
 c+=fl(5.5)+fl(3.5)+b'\x66'+fl(duration)+b'\x6e'+fl(60)+fl(60)+b'\x66\x6a'+fl(3.5)+b'\x62'
 c+=fl(5.5)+e.call('java/lang/Math','min','(FF)F')+fl(3.5)+e.call('java/lang/Math','max','(FF)F')+b'\x44'
 c+=e.out()+b'\x23'+e.call('java/lang/Float','isNaN','(F)Z')+e.call('java/io/PrintStream','println','(Z)V',182)
 c+=e.out()+b'\x23'+e.call('java/io/PrintStream','println','(F)V',182)
 c+=e.out()+b'\x23'+fl(40)+b'\x96\x9b\x00\x07\x03\xa7\x00\x04\x04'+e.call('java/io/PrintStream','println','(Z)V',182)
c+=b'\xb1';e.write(c)
weight=run('NativeWeightMathProbe',p)
assert 'duration=0\ntrue\nNaN\nfalse' in weight['stdout']
assert 'duration=60\nfalse\n3.5\ntrue' in weight['stdout']
oldzip=R/'release/0.1.1/EwingsAnimals-0.1.1-prototype-install.zip'
old=zipfile.ZipFile(oldzip).read('EwingsAnimals/42/media/lua/shared/Definitions/animal/EwingsAnimals_CatDefinitions.lua').decode()
assert '[adult] = { ageToGrow = 0 }' in old

client=(M/'lua/client/EwingsAnimals_Feeding.lua').read_text()
fixture='''
require=function() end
local callback
Events={OnFillWorldObjectContextMenu={Add=function(f) callback=f end}}
CharacterStat={HUNGER="hunger"};Perks={Strength="strength"}
instanceof=function(o,t) return o and o.class==t end
getText=function(k,...) return k end
local nativeFeed=function() end
AnimalContextMenu={onFeedAnimalFood=nativeFeed,cheat=false}
local function list(t) return {size=function() return #t end,isEmpty=function() return #t==0 end,get=function(s,i) return t[i+1] end} end
local function menu()
 local m={options={},subs={}}
 function m:addOption(name,target,fn,a,b) local o={name=name,target=target,fn=fn,a=a,b=b};table.insert(self.options,o);return o end
 function m:addSubMenu(o,s) o.subOption=#self.subs+1;self.subs[o.subOption]=s end
 function m:getSubMenu(n) return self.subs[n] end
 return m
end
ISContextMenu={getNew=function(s,parent) return menu() end}
local hunger=0.2;local kind="ewingsanimals_catadult";local currentWeight=4.5
local animal={class="IsoAnimal"}
function animal:getAnimalType() return kind end
function animal:isOnHook() return false end
function animal:isExistInTheWorld() return true end
function animal:canBeFeedByHand() return true end
function animal:getStats() return {get=function() return hunger end} end
function animal:getEatTypePossibleFromHand() return {contains=function(s,v) return v=="CatFood" or v=="Meat" or v=="Fish" or v=="Base.CatFoodBag" end} end
function animal:getData() return {getWeight=function() return currentWeight end} end
function animal:canBePicked(p) return true end
function animal:isWild() return false end
function animal:getBehavior() return {canBeAttached=function() return false end} end
local function food(cat,rotten,spice,fluid,feed)
 return {class="Food",getFluidContainer=function() return fluid end,isAnimalFeed=function() return feed end,isRotten=function() return rotten end,isSpice=function() return spice end,getHungerChange=function() return -0.1 end,getFoodType=function() return cat end,getMilkType=function() return nil end,getFullType=function() return "Base."..cat end,getDisplayName=function() return cat end}
end
local foods={food("CatFood"),food("Meat"),food("Fish"),food("Grass"),food("Meat",true),food("Meat",false,true),food("CatFood",false,false,true),food("CatFood",false,false,false,true)}
local player={getPerkLevel=function() return 5 end,getInventory=function() return {getAllEvalRecurse=function(self,pred) local t={} for _,f in ipairs(foods) do if pred(f) then table.insert(t,f) end end return list(t) end} end}
getSpecificPlayer=function() return player end
'''+client+'''
local function root() local c=menu();local sub=menu();local o=c:addOption("cat");o.onHighlightParams={animal};c:addSubMenu(o,sub);return c,sub end
for _,k in ipairs({"ewingsanimals_catadult","ewingsanimals_kitten"}) do
 kind=k;hunger=0.2;local c,sub=root();callback(0,c,{},false)
 assert(#sub.options==2 and sub.options[2].notAvailable)
 local offered=sub:getSubMenu(sub.options[1].subOption);assert(#offered.options==3)
 for _,o in ipairs(offered.options) do assert(o.target==player and o.fn==nativeFeed and o.a==animal and o.b.class=="Food") end
 callback(0,c,{},false);assert(#sub.options==2)
end
kind="raccoonsow";local c,sub=root();callback(0,c,{},false);assert(#sub.options==0)
kind="ewingsanimals_catadult";hunger=0.09;c,sub=root();callback(0,c,{},false);assert(#sub.options==1)
c,sub=root();callback(0,c,{},true);assert(#sub.options==0)
currentWeight=0/0;c,sub=root();callback(0,c,{},false);assert(#sub.options==1)
'''
p=P/'menu_assertions.lua';p.write_text(fixture,encoding='utf-8');menu=run('NativeLuaExec',p)
kitnode=M/'AnimSets/player/petanimal/petewingsanimalskitten.xml';node=ET.parse(kitnode).getroot()
assert node.findtext('m_Conditions/m_Value')=='ewingsanimals_kitten'
kitxml=run('NativeAnimNodeProbe',kitnode)
report={'version':'0.1.3','all_passed':True,'native_java_definitions':native,'native_jvm_weight_regression':weight,'cat_menu_stub_execution':menu,'kitten_xml_parser':kitxml,'native_raccoon_definition_sha256':sha(nativerac),'pickup_override_added':False,'rope_required':False,'acceptance_override_added':False,'adult_ids_preserved':True,'pickup_definition_bug':'0.1.1 adult stage duration zero causes native initWeight division by zero. At minAge, infinity times zero becomes NaN and fails weight < pickup limit. Set duration 60, matching terminal native raccoon adults.','live_missing_pickup_cause_confirmed':False,'limits':['Definition arithmetic bug reproduced offline; affected live cat weight not read.','No live world or multiplayer was run.','Menu event integration, native inventory conversion, kitten growth and existing saved cats require disposable-world testing.','Kittens reuse scaled original adult geometry; no juvenile-specific mesh is claimed.']}
(O/'behavior_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('BEHAVIOR_CHECKS_OK')
