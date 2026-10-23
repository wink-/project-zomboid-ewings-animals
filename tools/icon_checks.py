"""Native breed parsing, original icon pixels and native hand-render checks."""
from pathlib import Path
import hashlib,json,re,struct,subprocess,zipfile
import numpy as np
from inspect_native import GAME,sha
from native_probes import Emitter
from icon_pixels import read_png,write_png,resize,over
R=Path(__file__).resolve().parents[1];M=R/'stage/EwingsAnimals/42/media';O=R/'verification';P=R/'release/icon-checks';P.mkdir(parents=True,exist_ok=True)
VER=re.search(r'(?m)^version=(.+)$',(M.parent/'mod.info').read_text()).group(1).strip()
JAVA=GAME/'jre64/bin/java.exe';CP=str(O/'probes')+';'+str(GAME/'projectzomboid.jar')
def run(cls,path):
 p=subprocess.run([str(JAVA),'-cp',CP,cls,str(path)],capture_output=True,text=True,cwd=GAME,timeout=45)
 assert p.returncode==0,(cls,p.stdout,p.stderr)
 return {'exit_code':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}

e=Emitter('NativeIconBreedProbe')
base=(R/'tools/native_probes.py').read_text().split("e=Emitter('NativeLuaExec')")[1].split("c+=e.label('LUA_EXECUTION_OK')")[0]
scope={'e':e};exec(base,globals(),scope);c=scope['c']
c+=b'\x2b'+e.ins(179,e.field('zombie/Lua/LuaManager','env','Lse/krka/kahlua/vm/KahluaTable;'))
c+=e.call('zombie/characters/animals/AnimalDefinitions','loadAnimalDefinitions','()V')
c+=e.ins(19,e.string('ewingsanimals_catadult'))+e.call('zombie/characters/animals/AnimalDefinitions','getDef','(Ljava/lang/String;)Lzombie/characters/animals/AnimalDefinitions;')
c+=e.ins(19,e.string('ewingsanimals_browntabby'))+e.call('zombie/characters/animals/AnimalDefinitions','getBreedByName','(Ljava/lang/String;)Lzombie/characters/animals/datas/AnimalBreed;',182)+b'\x4e'
fields=['invIconMale','invIconFemale','invIconBaby','invIconMaleDead','invIconFemaleDead','invIconBabyDead']
for field in fields:
 c+=e.label(field)+e.out()+b'\x2d'+e.ins(180,e.field('zombie/characters/animals/datas/AnimalBreed',field,'Ljava/lang/String;'))+e.call('java/io/PrintStream','println','(Ljava/lang/String;)V',182)
c+=b'\xb1';e.write(c)
definition=(M/'lua/shared/Definitions/animal/EwingsAnimals_CatDefinitions.lua').read_text()
fixture='AnimalDefinitions={animals={}}\n'+(GAME/'media/lua/shared/Definitions/animal/AnimalGenomeDefinitions.lua').read_text()+definition
p=P/'native_icon_definitions.lua';p.write_text(fixture,encoding='utf-8');native=run('NativeIconBreedProbe',p)
lines=native['stdout'].splitlines();paths={}
for field in fields:
 path=lines[lines.index(field)+1];expected='media/textures/Item_EwingsCat_'+('Kitten' if 'Baby' in field else 'Adult')+'.png'
 assert path==expected
 rel=Path(path).relative_to('media');assert (M/rel).is_file()
 assert rel.as_posix() in {q.relative_to(M).as_posix() for q in M.rglob('*') if q.is_file()}
 paths[field]=path

oldzip=zipfile.ZipFile(R/'release/remote-v0.1.3-verified/EwingsAnimals-0.1.3-prototype-install.zip')
for q in (M/'lua').rglob('*.lua'):
 rel=q.relative_to(M).as_posix();old=oldzip.read('EwingsAnimals/42/media/'+rel).decode().replace('\r\n','\n')
 new=q.read_text().replace(VER,'0.1.3').replace('media/textures/Item_EwingsCat_Adult.png','Item_EwingsCat_Adult').replace('media/textures/Item_EwingsCat_Kitten.png','Item_EwingsCat_Adult')
 assert new==old,rel+' changed behavior beyond icon paths/version text'
assets={};images={}
for name in ['Adult','Kitten']:
 path=M/'textures'/('Item_EwingsCat_'+name+'.png');a=read_png(path);assert a.shape==(128,128,4)
 alpha=a[:,:,3];y,x=np.where(alpha>8);bounds=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
 assert min(bounds[:2])>=10 and max(bounds[2:])<=118
 assert alpha.min()==0 and alpha.max()==255 and np.count_nonzero(alpha>128)>1500
 assert not alpha[:10].any() and not alpha[-10:].any() and not alpha[:,:10].any() and not alpha[:,-10:].any()
 luminance=np.sum(a[:,:,:3]*np.array([.2126,.7152,.0722]),axis=2)/255
 assert float(np.median(luminance[alpha>200]))>.2,'Icon too dark on hand circle'
 small={}
 for size in [27,32,36,48,54,72,96]:
  s=resize(a,size,size);assert np.count_nonzero(s[:,:,3]>64)>40
  small[str(size)]={'nonempty_pixels':int(np.count_nonzero(s[:,:,3]>64))}
 assets[name]={'file':path.relative_to(R).as_posix(),'sha256':sha(path),'size':[128,128],'alpha_bounds_exclusive':bounds,'opaque_pixels':int(np.count_nonzero(alpha>128)),'median_visible_luminance':float(np.median(luminance[alpha>200])),'small_sizes':small}
 images[name]=a
assert assets['Adult']['sha256']!=assets['Kitten']['sha256']

# Native frame metadata only; no packed pixels are extracted or redistributed.
pack=(GAME/'media/texturepacks/UI2.pack').read_bytes();nativeframes={}
for name in ['Item_Raccoon','Item_Raccoon_Kit']:
 encoded=name.encode();start=0
 while True:
  at=pack.find(encoded,start);assert at>=0,name
  if struct.unpack_from('<I',pack,at-4)[0]==len(encoded):break
  start=at+len(encoded)
 values=struct.unpack_from('<8i',pack,at+len(encoded));nativeframes[name]={'trimmed_size':list(values[2:4]),'offset':list(values[4:6]),'original_size':list(values[6:8])}

ui=(GAME/'media/lua/client/ISUI/ISEquippedItem.lua').read_text()
snippet=ui[ui.index('\tif primaryItem then',ui.index('ISEquippedItem:render')):ui.index('    if self.chr:getBodyDamage()',ui.index('ISEquippedItem:render'))]
# Execute the real primary/secondary draw fragment with inert texture/UI stubs.
fixture='''
local function render(width)
 local TEXTURE_WIDTH=width;local TEXTURE_HEIGHT=width*0.75;local calls={}
 local texture={};local item={getTex=function() return texture end,getA=function() return 1 end,getR=function() return 1 end,getG=function() return 1 end,getB=function() return 1 end}
 local primaryItem=item;local secondaryItem=item
 local self={mainHand={x=0,y=0,width=width,height=width},offHand={x=0,y=width,width=width,height=width*0.75}}
 function self:drawTextureScaledAspect(tex,x,y,w,h,a,r,g,b) assert(tex==texture and a==1 and r==1 and g==1 and b==1);table.insert(calls,{w=w,h=h}) end
'''+snippet+'''
 assert(#calls==2 and calls[1].w==width*0.75 and calls[2].w==width*0.75*0.75)
end
for _,width in ipairs({48,64,80,96,128}) do render(width) end
'''
p=P/'native_hand_draw_assertions.lua';p.write_text(fixture,encoding='utf-8');draw=run('NativeLuaExec',p)

# Offline UI-scale sheet, using original approximated circles and real sizes.
# Top row adult, second kitten. Columns sidebar 48,64,96; P/S are hand slots.
sheet=np.full((430,840,4),255,np.uint8);sheet[:,:,:3]=45
font={'A':'01110/10001/10001/11111/10001/10001/10001','D':'11110/10001/10001/10001/10001/10001/11110','U':'10001/10001/10001/10001/10001/10001/01110','L':'10000/10000/10000/10000/10000/10000/11111','T':'11111/00100/00100/00100/00100/00100/00100','K':'10001/10010/10100/11000/10100/10010/10001','I':'11111/00100/00100/00100/00100/00100/11111','E':'11111/10000/10000/11110/10000/10000/11111','N':'10001/11001/10101/10011/10001/10001/10001','P':'11110/10001/10001/11110/10000/10000/10000','S':'01111/10000/10000/01110/00001/00001/11110','2':'01110/10001/00001/00010/00100/01000/11111','3':'11110/00001/00001/01110/00001/00001/11110','4':'00010/00110/01010/10010/11111/00010/00010','6':'01110/10000/10000/11110/10001/10001/01110','8':'01110/10001/10001/01110/10001/10001/01110','9':'01110/10001/10001/01111/00001/00001/01110'}
def text(s,x,y,scale=2):
 for letter in s:
  if letter!=' ':
   for j,row in enumerate(font[letter].split('/')):
    for i,v in enumerate(row):
     if v=='1':sheet[y+j*scale:y+(j+1)*scale,x+i*scale:x+(i+1)*scale,:3]=220
  x+=6*scale
def ellipse(x,y,w,h):
 yy,xx=np.mgrid[:h,:w];d=((xx-(w-1)/2)/(w/2))**2+((yy-(h-1)/2)/(h/2))**2
 view=sheet[y:y+h,x:x+w];view[d<=1,:3]=95;view[d<.85,:3]=8
for row,name in enumerate(['Adult','Kitten']):
 text(name.upper(),8,85+row*150,1)
 for col,width in enumerate([48,64,96]):
  x=90+col*240;y=50+row*150
  if row==0:text(str(width),x+70,12)
  text('P',x+40,y+112,1);text('S',x+160,y+112,1)
  for index in [0,1]:
   w=width;h=width if index==0 else round(width*.75);bx=x+index*120+(96-w)//2;by=y+(96-h)//2
   ellipse(bx,by,w,h);size=round(width*.75*(1 if index==0 else .75));over(sheet,resize(images[name],size,size),bx+(w-size)//2,by+(h-size)//2)
text('32',20,365)
for i,name in enumerate(['Adult','Kitten']):over(sheet,resize(images[name],32,32),100+i*100,355)
preview=R/'previews/EwingsAnimals_hand_icons_preview.png';write_png(preview,sheet)
report={'version':VER,'all_passed':True,'cause':'Bare unregistered pack-style icon names passed directly to Texture.getSharedTexture; loose PNG lookup needs complete media/textures path and extension.','native_breed_parser':native,'native_hand_render_fragment':draw,'breed_paths':paths,'icons':assets,'native_frame_metadata':nativeframes,'behavior_preserved_from_0_1_3':True,'global_base_animal_or_ui_override':False,'ui_preview':preview.relative_to(R).as_posix(),'user_reported_kitten_pickup_on_0_1_3':True,'runtime_icon_tested':False,'multiplayer_tested':False,'limits':['Native breed parser and hand draw fragment use isolated execution, not a rendered game UI.','GPU texture upload and mod VFS loading require a restarted disposable game test.','Already held items may need drop/pickup after restart for native icon initialization.']}
(O/'icon_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('ICON_CHECKS_OK',json.dumps({k:v['alpha_bounds_exclusive'] for k,v in assets.items()}))
