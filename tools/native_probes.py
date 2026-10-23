"""Emit tiny JVM asset/parser probes without installing a compiler.

Equivalent Java source is embedded below. These classes invoke ONLY Assimp's
asset importer or Kahlua's Lua compiler; they never start Project Zomboid.
"""
from pathlib import Path
import struct
from inspect_native import GAME
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/probes';OUT.mkdir(parents=True,exist_ok=True)
def u2(n):return struct.pack('>H',n)
def u4(n):return struct.pack('>I',n)
class Emitter:
    def __init__(self,name):self.pool=[];self.name=name;self.cache={}
    def cp(self,key,data):
        if key not in self.cache:self.pool.append(data);self.cache[key]=len(self.pool)
        return self.cache[key]
    def utf(self,s):return self.cp(('u',s),b'\x01'+u2(len(s.encode()))+s.encode())
    def cls(self,s):return self.cp(('c',s),b'\x07'+u2(self.utf(s)))
    def nt(self,n,d):return self.cp(('nt',n,d),b'\x0c'+u2(self.utf(n))+u2(self.utf(d)))
    def method(self,c,n,d,interface=False):return self.cp(('m',c,n,d,interface),bytes([11 if interface else 10])+u2(self.cls(c))+u2(self.nt(n,d)))
    def field(self,c,n,d):return self.cp(('f',c,n,d),b'\x09'+u2(self.cls(c))+u2(self.nt(n,d)))
    def string(self,s):return self.cp(('s',s),b'\x08'+u2(self.utf(s)))
    def ins(self,op,index):return bytes([op])+u2(index)
    def call(self,c,n,d,op=184):return self.ins(op,self.method(c,n,d))
    def out(self):return self.ins(178,self.field('java/lang/System','out','Ljava/io/PrintStream;'))
    def label(self,s):return self.out()+self.ins(19,self.string(s))+self.call('java/io/PrintStream','println','(Ljava/lang/String;)V',182)
    def printlnint(self):return self.call('java/io/PrintStream','println','(I)V',182)
    def write(self,code):self.write_methods([('main','([Ljava/lang/String;)V',0x0009,code)])
    def write_methods(self,specs,base_name='java/lang/Object'):
        this=self.cls(self.name);base=self.cls(base_name);cn=self.utf('Code');methods=[]
        for name,descriptor,access,code in specs:
            n=self.utf(name);d=self.utf(descriptor);body=u2(12)+u2(8)+u4(len(code))+code+u2(0)+u2(0)
            methods.append(u2(access)+u2(n)+u2(d)+u2(1)+u2(cn)+u4(len(body))+body)
        data=b'\xca\xfe\xba\xbe'+u2(0)+u2(49)+u2(len(self.pool)+1)+b''.join(self.pool)+u2(0x0021)+u2(this)+u2(base)+u2(0)+u2(0)+u2(len(methods))+b''.join(methods)+u2(0)
        (OUT/(self.name+'.class')).write_bytes(data)

e=Emitter('NativeAbsoluteLoader')
ctor=b'\x2a'+e.call('jassimp/JassimpLibraryLoader','<init>','()V',183)+b'\xb1'
load=e.ins(19,e.string(str(GAME/'jassimp64.dll')))+e.call('java/lang/System','load','(Ljava/lang/String;)V')+b'\xb1'
e.write_methods([('<init>','()V',1,ctor),('loadLibrary','()V',1,load)],'jassimp/JassimpLibraryLoader')

e=Emitter('NativeMeshProbe')
# AiScene scene=Jassimp.importFile(args[0]); report scene/mesh counts.
c=e.ins(187,e.cls('NativeAbsoluteLoader'))+b'\x59'+e.call('NativeAbsoluteLoader','<init>','()V',183)+e.call('jassimp/Jassimp','setLibraryLoader','(Ljassimp/JassimpLibraryLoader;)V')
c+=b'\x2a\x03\x32'+e.call('jassimp/Jassimp','importFile','(Ljava/lang/String;)Ljassimp/AiScene;')+b'\x4c'
c+=e.label('MESHES')+e.out()+b'\x2b'+e.call('jassimp/AiScene','getNumMeshes','()I',182)+e.printlnint()
c+=b'\x2b'+e.call('jassimp/AiScene','getMeshes','()Ljava/util/List;',182)+b'\x03'+e.ins(185,e.method('java/util/List','get','(I)Ljava/lang/Object;',True))+b'\x02\x00'+e.ins(192,e.cls('jassimp/AiMesh'))+b'\x4d'
for label,method in [('VERTICES','getNumVertices'),('FACES','getNumFaces')]:c+=e.label(label)+e.out()+b'\x2c'+e.call('jassimp/AiMesh',method,'()I',182)+e.printlnint()
c+=e.label('BONES')+e.out()+b'\x2c'+e.call('jassimp/AiMesh','getBones','()Ljava/util/List;',182)+e.ins(185,e.method('java/util/List','size','()I',True))+b'\x01\x00'+e.printlnint()
c+=e.label('ANIMATIONS')+e.out()+b'\x2b'+e.call('jassimp/AiScene','getNumAnimations','()I',182)+e.printlnint()+b'\xb1'
e.write(c)

e=Emitter('NativeLuaProbe')
# LuaCompiler.loadis(new FileInputStream(args[0]),args[0],null);
c=e.ins(187,e.cls('java/io/FileInputStream'))+b'\x59\x2a\x03\x32'+e.call('java/io/FileInputStream','<init>','(Ljava/lang/String;)V',183)
c+=b'\x2a\x03\x32\x01'+e.call('se/krka/kahlua/luaj/compiler/LuaCompiler','loadis','(Ljava/io/InputStream;Ljava/lang/String;Lse/krka/kahlua/vm/KahluaTable;)Lse/krka/kahlua/vm/LuaClosure;')+b'\x57'
c+=e.label('LUA_COMPILE_OK')+b'\xb1';e.write(c)
print('Emitted isolated native parser probes in',OUT)

e=Emitter('NativeLuaExec')
c=e.call('se/krka/kahlua/j2se/J2SEPlatform','getInstance','()Lse/krka/kahlua/j2se/J2SEPlatform;')+e.call('se/krka/kahlua/j2se/J2SEPlatform','newEnvironment','()Lse/krka/kahlua/vm/KahluaTable;',182)+b'\x4c'
c+=e.ins(187,e.cls('se/krka/kahlua/vm/KahluaThread'))+b'\x59'+e.call('se/krka/kahlua/j2se/J2SEPlatform','getInstance','()Lse/krka/kahlua/j2se/J2SEPlatform;')+b'\x2b'+e.call('se/krka/kahlua/vm/KahluaThread','<init>','(Lse/krka/kahlua/vm/Platform;Lse/krka/kahlua/vm/KahluaTable;)V',183)+b'\x4d'
c+=e.ins(187,e.cls('java/io/FileInputStream'))+b'\x59\x2a\x03\x32'+e.call('java/io/FileInputStream','<init>','(Ljava/lang/String;)V',183)+b'\x2a\x03\x32\x2b'+e.call('se/krka/kahlua/luaj/compiler/LuaCompiler','loadis','(Ljava/io/InputStream;Ljava/lang/String;Lse/krka/kahlua/vm/KahluaTable;)Lse/krka/kahlua/vm/LuaClosure;')+b'\x4e'
c+=b'\x2c\x2d\x01\x01\x01'+e.call('se/krka/kahlua/vm/KahluaThread','call','(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;',182)+b'\x57'
c+=e.label('LUA_EXECUTION_OK')+b'\xb1';e.write(c)

e=Emitter('NativeScriptProbe')
c=e.ins(187,e.cls('java/lang/String'))+b'\x59'+e.ins(187,e.cls('java/io/FileInputStream'))+b'\x59\x2a\x03\x32'+e.call('java/io/FileInputStream','<init>','(Ljava/lang/String;)V',183)+e.call('java/io/FileInputStream','readAllBytes','()[B',182)+e.call('java/lang/String','<init>','([B)V',183)
c+=e.call('zombie/scripting/ScriptParser','parse','(Ljava/lang/String;)Lzombie/scripting/ScriptParser$Block;')+b'\x57'+e.label('MODEL_SCRIPT_PARSE_OK')+b'\xb1';e.write(c)

e=Emitter('NativeAnimNodeProbe')
c=b'\x2a\x03\x32'+e.call('zombie/core/skinnedmodel/advancedanimation/AnimNode','Parse','(Ljava/lang/String;)Lzombie/core/skinnedmodel/advancedanimation/AnimNode;')
c+=e.call('java/util/Objects','requireNonNull','(Ljava/lang/Object;)Ljava/lang/Object;')+b'\x57'+e.label('ANIM_NODE_PARSE_OK')+b'\xb1';e.write(c)
