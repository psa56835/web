# v4 動態繪本主渲染
# python3 render.py out.mp4 vo資料夾 [--fast] [--only 3]
import os, sys, json, math, re, numpy as np, soundfile as sf
from PIL import Image, ImageFilter
from engine import *

PRE, POST, XF = 0.35, 0.55, 0.45        # 語音前後留白、鏡頭溶接秒數
out, vo = sys.argv[1], sys.argv[2]
FAST = '--fast' in sys.argv
ONLY = int(sys.argv[sys.argv.index('--only') + 1]) if '--only' in sys.argv else None
LINES = json.load(open('lines.json'))

# ---------- 語音與子句時間 ----------
def phrase_starts(y, sr, n):
    fr = int(sr * .01)
    e = np.array([np.abs(y[i:i + fr]).max() for i in range(0, len(y) - fr, fr)]) > 0.015
    gaps, i = [], 0
    while i < len(e):
        if not e[i]:
            j = i
            while j < len(e) and not e[j]:
                j += 1
            if 0 < i and j < len(e):
                gaps.append((j - i, j))
            i = j
        else:
            i += 1
    cut = sorted(g[1] for g in sorted(gaps, reverse=True)[:n - 1])
    return [PRE + k * .01 for k in [int(np.argmax(e))] + cut]

clips, P, D = [], [], []
for i in range(1, 7):
    y, sr = sf.read(f'{vo}/l{i}.wav'); y = y if y.ndim == 1 else y.mean(1)
    n = len(re.findall(r'[^，、。！？]+[，、。！？]', LINES[str(i)]))
    clips.append(y); P.append(phrase_starts(y, sr, n)); D.append(len(y) / sr + PRE + POST)
D[-1] += 1.0
print('段長', [round(d, 2) for d in D], '總長', round(sum(D), 2))

# ---------- 素材 ----------
SRC1 = Image.open('../src/ref/scene1.png').convert('RGB')
S1 = SRC1.resize((round(W * 1.08), round(SRC1.height * W * 1.08 / SRC1.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 50, 2)).convert('RGBA')
SUN = Image.open('assets/sun.png').convert('RGBA')

@lru_cache(64)
def sun_img(h, rot):
    s = SUN.resize((max(1, round(SUN.width * h / SUN.height)), max(1, h)), Image.LANCZOS)
    return s.rotate(rot, Image.BICUBIC, expand=True) if rot else s

def put_sun(f, x, y, h, rot=0, a=1.0):
    s = sun_img(int(h), round(rot))
    if a < 1:
        s = s.copy(); s.putalpha(s.getchannel('A').point(lambda v: int(v * a)))
    glow(f, x, y, h * 1.1, (255, 226, 150), 0.55 * a)
    f.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2))) if x - s.width / 2 >= 0 and y - s.height / 2 >= 0 else f.paste(s, (int(x - s.width / 2), int(y - s.height / 2)), s)

# ---------- 鏡頭：plate + 推移 + 角色層定格漂浮 ----------
def shot(name, t, d, z0=1.0, z1=1.06, c0=(.5, .5), c1=(.5, .5), bob=8, fz=0.03, lift=0):
    bg, fg = plate(f'plates/{name}.png')
    u = ease(t / d)
    z = z0 + (z1 - z0) * u; cx = c0[0] + (c1[0] - c0[0]) * u; cy = c0[1] + (c1[1] - c0[1]) * u
    f, (l, tp, k) = view(bg, z, cx, cy)
    if fg is not None:
        ts = step12(t)
        zz = z * (1 + fz * u)
        c = fg.resize((round(fg.width * zz), round(fg.height * zz)), Image.BICUBIC)
        # 角色層以同一個鏡頭中心放大多一點（視差）+ 定格上下漂浮
        ox = W / 2 - cx * fg.width * zz; oy = H / 2 - cy * fg.height * zz - bob * abs(math.sin(ts * 3.2)) - lift * u
        f.alpha_composite(c, (0, 0), (int(-ox), int(-oy), int(-ox) + W, int(-oy) + H)) if ox <= 0 and oy <= 0 else f.paste(c, (int(ox), int(oy)), c)
    return f

def to_frame(fx, fy, name, t, d, **kw):  # plate 內比例座標 → 畫面座標（近似，忽略視差）
    bg, _ = plate(f'plates/{name}.png')
    z0, z1 = kw.get('z0', 1.0), kw.get('z1', 1.06); c0, c1 = kw.get('c0', (.5, .5)), kw.get('c1', (.5, .5))
    u = ease(t / d); z = z0 + (z1 - z0) * u; cx = c0[0] + (c1[0] - c0[0]) * u; cy = c0[1] + (c1[1] - c0[1]) * u
    return W / 2 + (fx - cx) * bg.width * z, H / 2 + (fy - cy) * bg.height * z, z

# ---------- 各幕 ----------
def scene1(t, d, p):
    z = 1.0 + 0.07 * ease(t / d)
    cw, ch = S1.width / z / 1.08, S1.height / z / 1.08
    l, tp = (S1.width - cw) * .45, (S1.height - ch) * .4
    f = S1.resize((W, round(W * S1.height / S1.width)), Image.BICUBIC, box=(l, tp, l + cw, tp + ch * 1.0))
    f = f.resize((W, H), Image.BICUBIC) if f.height != H else f
    glow(f, 196 * 1.15, 184 * 1.15, 170, (255, 244, 220), 0.25 + 0.12 * math.sin(t * 1.6))
    glow(f, 985, 590, 130, (255, 214, 150), 0.25 + 0.12 * math.sin(t * 2.1 + 1))
    sparkles(f, t, 18, 1, (100, 250, 1000, 900), 25, size=(3, 7))
    return f

SUN2 = [(.22, .16), (.45, .11), (.70, .14), (.86, .24), (.33, .27), (.58, .24), (.14, .33), (.47, .38), (.76, .35), (.62, .45)]
def scene2(t, d, p):
    tb = p[2] - .2
    def A(tt):
        kw = dict(z0=1.08, z1=1.0, c0=(.5, .4), c1=(.5, .5))
        f = shot('s2a', tt, tb + XF, **kw)
        for i, (x, y) in enumerate(SUN2):
            s = seg(tt, p[1] + i * .13, p[1] + i * .13 + .45)
            if s > 0:
                X, Y, z = to_frame(x, y, 's2a', tt, tb + XF, **kw)
                put_sun(f, X, Y + 8 * math.sin(tt * 2.5 + i), 150 * z * (0.2 + 0.8 * min(1, s * 1.25) - 0.1 * math.sin(min(s, 1) * math.pi)), 8 * math.sin(tt * 2 + i))
        tint(f, (255, 170, 100), 0.06 + 0.04 * math.sin(tt * 3))
        return f
    def B(tt):
        f = shot('s2b', tt, d - tb, z0=1.0, z1=1.07, c0=(.5, .45), c1=(.5, .42), bob=6)
        tint(f, (255, 160, 90), 0.08 + 0.05 * math.sin(tt * 3))
        sparkles(f, tt, 14, 5, (0, 900, W, 1600), -40, col=(255, 250, 235), size=(3, 6))  # 熱浪光點往上
        return f
    return xfade(t, tb, A, B)

def xfade(t, tb, A, B):
    if t < tb:
        return A(t)
    if t < tb + XF:
        k = ease((t - tb) / XF); a, b = A(t), B(t - tb)
        return Image.blend(a, b, k)
    return B(t - tb)

# 其餘幕在素材定稿後補上
SCENES = [scene1, scene2]

if __name__ == '__main__':
    audio = None
    tr = np.zeros(int(sum(D) * sr) + sr); t0 = 0
    for c, d in zip(clips, D):
        s = int((t0 + PRE) * sr); tr[s:s + len(c)] += c; t0 += d
    audio = out + '.wav'; sf.write(audio, tr[:int(sum(D) * sr)], sr)
    wr = Writer(out, None if ONLY else audio)
    prev = None
    for si, d in enumerate(D[:len(SCENES)]):
        if ONLY and si + 1 != ONLY:
            continue
        n = int(round(d * FPS)); stp = 3 if FAST else 1
        for k in range(0, n, stp):
            t = k / FPS
            im = SCENES[si](t, d, P[si]).convert('RGB')
            for _ in range(min(stp, n - k)):
                wr.write(im)
        print('scene', si + 1, 'ok', flush=True)
    wr.close(); os.remove(audio); print('done', out)
