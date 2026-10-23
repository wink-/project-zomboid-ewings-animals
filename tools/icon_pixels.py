"""Small PNG/alpha helpers for original model-derived icons; no extra packages."""
import struct,zlib
import numpy as np

def read_png(path):
    b=path.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';p=8;compressed=bytearray()
    while p<len(b):
        n=struct.unpack_from('>I',b,p)[0];kind=b[p+4:p+8];data=b[p+8:p+8+n]
        assert zlib.crc32(kind+data)&0xffffffff==struct.unpack_from('>I',b,p+8+n)[0]
        if kind==b'IHDR':w,h,depth,color,_,_,interlace=struct.unpack('>IIBBBBB',data)
        if kind==b'IDAT':compressed.extend(data)
        p+=12+n
    assert depth==8 and color==6 and interlace==0
    raw=zlib.decompress(compressed);stride=w*4;rows=[];prior=bytearray(stride);pos=0
    for y in range(h):
        mode=raw[pos];pos+=1;row=bytearray(raw[pos:pos+stride]);pos+=stride
        for x in range(stride):
            a=row[x-4] if x>=4 else 0;b=prior[x];c=prior[x-4] if x>=4 else 0
            if mode==1:predict=a
            elif mode==2:predict=b
            elif mode==3:predict=(a+b)//2
            elif mode==4:
                estimate=a+b-c;dist=[abs(estimate-a),abs(estimate-b),abs(estimate-c)];predict=[a,b,c][dist.index(min(dist))]
            else:assert mode==0;predict=0
            row[x]=(row[x]+predict)&255
        rows.append(bytes(row));prior=row
    assert pos==len(raw)
    return np.frombuffer(b''.join(rows),dtype=np.uint8).reshape(h,w,4).copy()

def write_png(path,a):
    a=np.asarray(a,dtype=np.uint8);h,w,_=a.shape
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    raw=b''.join(b'\0'+r.tobytes() for r in a)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'sRGB',b'\0')+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))

def resize(a,w,h):
    p=a.astype(float)/255;alpha=p[:,:,3:4]
    p[:,:,:3]=np.where(p[:,:,:3]<=.04045,p[:,:,:3]/12.92,((p[:,:,:3]+.055)/1.055)**2.4)*alpha
    x=np.clip((np.arange(w)+.5)*p.shape[1]/w-.5,0,p.shape[1]-1);y=np.clip((np.arange(h)+.5)*p.shape[0]/h-.5,0,p.shape[0]-1)
    x0=x.astype(int);x1=np.minimum(x0+1,p.shape[1]-1);tx=(x-x0)[None,:,None]
    y0=y.astype(int);y1=np.minimum(y0+1,p.shape[0]-1);ty=(y-y0)[:,None,None]
    q=p[:,x0]*(1-tx)+p[:,x1]*tx;q=q[y0]*(1-ty)+q[y1]*ty
    rgb=np.divide(q[:,:,:3],q[:,:,3:4],out=np.zeros_like(q[:,:,:3]),where=q[:,:,3:4]>1e-8)
    q[:,:,:3]=np.where(rgb<=.0031308,rgb*12.92,1.055*np.maximum(rgb,0)**(1/2.4)-.055)
    return np.clip(np.rint(q*255),0,255).astype(np.uint8)

def padded_icon(raw):
    y,x=np.where(raw[:,:,3]>8);crop=raw[y.min():y.max()+1,x.min():x.max()+1]
    factor=104/max(crop.shape[:2]);w=round(crop.shape[1]*factor);h=round(crop.shape[0]*factor)
    icon=np.zeros((128,128,4),np.uint8);x=(128-w)//2;y=(128-h)//2;icon[y:y+h,x:x+w]=resize(crop,w,h)
    return icon

def over(canvas,icon,x,y):
    h,w=icon.shape[:2];bg=canvas[y:y+h,x:x+w].astype(float);a=icon[:,:,3:4]/255
    bg[:,:,:3]=icon[:,:,:3]*a+bg[:,:,:3]*(1-a);bg[:,:,3]=255;canvas[y:y+h,x:x+w]=np.rint(bg).astype(np.uint8)
