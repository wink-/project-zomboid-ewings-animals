"""Losslessly remove textual/EXIF metadata from original project PNGs."""
from pathlib import Path
import struct,hashlib,json,zlib
DROP={b'tEXt',b'zTXt',b'iTXt',b'eXIf'}
def sanitize_tree(root):
    root=Path(root);records=[]
    paths=list((root/'previews').glob('*.png'))+list((root/'stage/EwingsAnimals/42/media/textures').rglob('*.png'))
    for path in sorted(paths):
        raw=path.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';out=bytearray(raw[:8]);p=8;idat=bytearray();removed=[]
        while p<len(raw):
            n=struct.unpack('>I',raw[p:p+4])[0];typ=raw[p+4:p+8];data=raw[p+8:p+8+n];chunk=raw[p:p+n+12]
            assert zlib.crc32(typ+data)&0xffffffff==struct.unpack('>I',raw[p+8+n:p+12+n])[0]
            if typ==b'IDAT':idat.extend(data)
            if typ in DROP:removed.append(typ.decode())
            else:out.extend(chunk)
            p+=n+12
        assert p==len(raw)
        if removed:path.write_bytes(out)
        records.append({'file':path.relative_to(root).as_posix(),'removed_metadata_chunks':removed,'unchanged_compressed_pixel_sha256':hashlib.sha256(idat).hexdigest()})
    (root/'verification/png_sanitization.json').write_text(json.dumps(records,indent=2)+'\n')
    return records
if __name__=='__main__':
    r=sanitize_tree(Path(__file__).resolve().parents[1]);print('PNG_METADATA_SANITIZED',len(r))
