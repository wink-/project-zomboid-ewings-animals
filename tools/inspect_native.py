"""Read-only inspection of installed .x rig metadata. Never copies native meshes."""
import json, re, hashlib, pathlib, sys, os
import numpy as np

if not os.environ.get('PZ_GAME_DIR'):
    raise RuntimeError('Set PZ_GAME_DIR to your installed Project Zomboid directory.')
GAME = pathlib.Path(os.environ['PZ_GAME_DIR']).expanduser().resolve()
NUMBER = r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?'

def block_end(text, start):
    depth = 1
    for i in range(start + 1, len(text)):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if not depth: return i
    raise ValueError('Unclosed .x block')

def frames(path):
    text = pathlib.Path(path).read_text()
    result = {}
    spans = []
    for m in re.finditer(r'\bFrame\s+(\w+)\s*\{', text):
        end = block_end(text, m.end()-1)
        mat = re.match(r'\s*FrameTransformMatrix\s*\{([^}]+)', text[m.end():])
        if not mat: continue
        vals = [float(x) for x in re.findall(NUMBER, mat[1])]
        assert len(vals) == 16
        parents = [(a,b,n) for a,b,n in spans if a < m.start() < b]
        parent = max(parents, default=(0,0,None))[2]
        result[m[1]] = {'parent': parent, 'local': np.array(vals).reshape(4,4).T}
        spans.append((m.start(), end, m[1]))
    for name, f in result.items():
        f['global'] = result[f['parent']]['global'] @ f['local'] if f['parent'] else f['local']
    return result

def skin_offsets(path):
    text = pathlib.Path(path).read_text()
    result = {}
    for m in re.finditer(r'\bSkinWeights\s*\{\s*"([^"]+)"\s*;', text):
        body = text[m.end():block_end(text,m.end()-1)]
        # Last sixteen numeric values are the inverse bind matrix.
        vals = [float(x) for x in re.findall(NUMBER, body)]
        result[m[1]] = np.array(vals[-16:]).reshape(4,4).T
    return result

def animation(path):
    text = pathlib.Path(path).read_text()
    tracks = {}
    for m in re.finditer(r'\bAnimation\s*\{\s*\{\s*(\w+)\s*\}', text):
        end = block_end(text, text.index('{', m.start()))
        body = text[m.end():end]
        keys = {}
        for k in re.finditer(r'AnimationKey\s+\w+\s*\{([^}]+)', body):
            nums = [float(x) for x in re.findall(NUMBER, k[1])]
            typ, count = int(nums[0]), int(nums[1]); p = 2; rows=[]
            for _ in range(count):
                t,n=int(nums[p]),int(nums[p+1]); p+=2
                rows.append((t,nums[p:p+n]));p+=n
            keys[typ] = rows
        tracks[m[1]] = keys
    ticks = re.search(r'AnimTicksPerSecond\s*\{\s*(\d+)',text)
    return tracks, int(ticks[1]) if ticks else 4800

def sha(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

if __name__ == '__main__':
    path = GAME/'media/models_X/Skinned/Raccoon_Body.x'
    ff=frames(path); offsets=skin_offsets(path)
    for n,f in ff.items():
        p=f['global'][:3,3]
        error=float(np.max(np.abs(f['global']@offsets[n]-np.eye(4)))) if n in offsets else None
        print(n, f['parent'], [round(float(x),5) for x in p], 'bind_error',error)
    print('sha256',sha(path))
