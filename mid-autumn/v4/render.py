# v4 動態繪本主渲染
# python3 render.py out.mp4 vo資料夾 [--fast] [--only 3]
import os, sys, json, math, re, numpy as np, soundfile as sf
from PIL import Image, ImageFilter
from engine import *

PRE, POST, XF = 0.25, 0.35, 0.45        # 語音前後留白、鏡頭溶接秒數
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
_hy = np.linspace(1, 0, H)[:, None] ** 1.6
HEAT = Image.fromarray(np.dstack([np.full((H, W), 255), np.full((H, W), 205), np.full((H, W), 130), (np.repeat(_hy, W, 1) * 90 * (np.arange(H)[:, None] < 900)).astype(np.uint8)]).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(40))
PX = lambda X, Y: ((X + 65) / 1210, (Y + 115) / 2150)   # 畫面座標(z=1) → plate 比例座標

@lru_cache(64)
def sun_img(h, rot):
    s = SUN.resize((max(1, round(SUN.width * h / SUN.height)), max(1, h)), Image.LANCZOS)
    return s.rotate(rot, Image.BICUBIC, expand=True) if rot else s

def put_sun(f, x, y, h, rot=0, a=1.0):
    s = sun_img(int(h), round(rot))
    if a < 1:
        s = s.copy(); s.putalpha(s.getchannel('A').point(lambda v: int(v * a)))
    glow(f, x, y, h * 1.5, (255, 214, 120), 0.8 * a)
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

SUN2 = [(170, 200), (410, 160), (660, 180), (900, 230), (290, 350), (540, 320), (790, 370), (150, 500), (420, 490), (680, 520)]
def scene2(t, d, p):
    tb = p[3] - .2
    def A(tt):
        kw = dict(z0=1.0, z1=1.05, c0=(.5, .47), c1=(.5, .5))
        f = shot('s2a', tt, tb + XF, **kw)
        for i, (x, y) in enumerate(SUN2):
            s = seg(tt, p[1] + i * .13, p[1] + i * .13 + .45)
            if s > 0:
                X, Y, z = to_frame(*PX(x, y), 's2a', tt, tb + XF, **kw)
                put_sun(f, X, Y + 8 * math.sin(tt * 2.5 + i), 190 * z * (0.2 + 0.8 * min(1, s * 1.25) - 0.1 * math.sin(min(s, 1) * math.pi)), 8 * math.sin(tt * 2 + i))
        f.alpha_composite(HEAT)
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

def seq(t, shots):  # shots=[(開始秒, fn(tt, 長度))]，相鄰鏡頭交叉溶接
    for i in range(len(shots) - 1, -1, -1):
        if t >= shots[i][0]:
            break
    st, fn, dur = shots[i]
    if i > 0 and t < st + XF:
        pst, pfn, pdur = shots[i - 1]
        return Image.blend(pfn(t - pst, pdur), fn(t - st, dur), ease((t - st) / XF))
    return fn(t - st, dur)

def mk(bounds, fns, d):
    return [(b, f, (bounds[i + 1] if i + 1 < len(bounds) else d) - b + XF) for i, (b, f) in enumerate(zip(bounds, fns))]

# ---------- 3 后羿射日 ----------
SUN3 = [(170, 260), (420, 190), (700, 230), (930, 300), (280, 420), (560, 380), (820, 470), (150, 580), (440, 600), (720, 640)]
KEEP = 6
def scene3(t, d, p):
    shots_at = [0, p[3] - .15, p[8] - .15]
    hits = {4: (0, 3, 7), 5: (1, 4, 8), 6: (2, 5, 9)}
    def A(tt, dd):
        f = shot('s3a', tt, dd, z0=1.0, z1=1.08, c0=(.5, .56), c1=(.5, .5), bob=10)
        return f
    def B(tt, dd):
        T = tt + shots_at[1]
        f = shot('s3b', tt, dd, z0=1.02, z1=1.0, c0=(.5, .5), c1=(.5, .52), bob=6)
        for i, (x, y) in enumerate(SUN3):
            hit = next((p[k] + .3 + j * .07 for k, ids in hits.items() for j, q in enumerate(ids) if q == i), None)
            bob = 8 * math.sin(T * 2.5 + i)
            if hit is None or T < hit:
                put_sun(f, x, y + bob, 165, 8 * math.sin(T * 2 + i))
            elif T < hit + .9:
                k = (T - hit) / .9
                put_sun(f, x + 90 * k, y + bob + 700 * k * k, 165 * (1 - .4 * k), 360 * k, 1 - k)
        for k, ids in hits.items():  # 箭
            for j, q in enumerate(ids):
                s0 = p[k] + j * .07; s1 = s0 + .3
                if s0 <= T < s1:
                    arrow(f, 400, 560, *SUN3[q], (T - s0) / .3)
                if s1 <= T < s1 + .6:
                    burst(f, *SUN3[q], (T - s1) / .6)
        return f
    def C(tt, dd):
        T = tt + shots_at[2]
        f = shot('s3c', tt, dd, z0=1.0, z1=1.06, c0=(.5, .5), c1=(.5, .47), bob=8)
        wk = seg(T, p[9], p[9] + 2.0); dip = math.sin(math.pi * wk)
        tint(f, (60, 50, 110), .35 * dip)
        put_sun(f, 820, 330 + 330 * dip, 150 - 30 * dip, 6 * math.sin(T * 2))
        return f
    return seq(t, mk(shots_at, [A, B, C], d))

def arrow(f, x0, y0, x1, y1, k):
    x, y = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k; a = math.atan2(y1 - y0, x1 - x0)
    dx, dy = math.cos(a), math.sin(a)
    lay = Image.new('RGBA', f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line((x - dx * 380, y - dy * 380, x - dx * 60, y - dy * 60), fill=(255, 246, 215, 200), width=40)
    lay = lay.filter(ImageFilter.GaussianBlur(8)); d = ImageDraw.Draw(lay)
    d.line((x - dx * 130, y - dy * 130, x, y), fill=(120, 80, 60, 255), width=13)
    d.polygon([(x + dx * 34, y + dy * 34), (x - dy * 15, y + dx * 15), (x + dy * 15, y - dx * 15)], fill=(233, 185, 106, 255))
    f.alpha_composite(lay)

# ---------- 4 當國王、變兇、拿仙丹 ----------
def scene4(t, d, p):
    shots_at = [0, p[2] - .2]
    def A(tt, dd):
        f = shot('s4a', tt, dd, z0=1.0, z1=1.06, c0=(.5, .5), c1=(.5, .47), bob=14)
        sparkles(f, tt, 36, 9, (90, 200, 990, 1400), -120, col=(255, 226, 170), size=(6, 12))  # 彩帶光點往下灑
        return f
    def B(tt, dd):
        T = tt + shots_at[1]
        pill = seg(T, p[3], p[3] + 1.2)
        f = shot('s4b', tt, dd, z0=1.0, z1=1.0 + .12 * pill, c0=(.5, .5), c1=PX(380, 740), bob=4)
        ang = seg(T, p[2], p[2] + .4) * (1 - seg(T, p[3] - .2, p[3] + .4))
        if ang > 0:
            sh = int(10 * ang * math.sin(T * 48))
            f = f.transform(f.size, Image.AFFINE, (1, 0, sh, 0, 1, 0), Image.BICUBIC)
            tint(f, (120, 30, 40), .18 * ang); vignette(f, .6 * ang)
        if pill > 0:
            X, Y, z = to_frame(*PX(332, 740), 's4b', tt, dd, z0=1.0, z1=1.0 + .12 * pill, c0=(.5, .5), c1=PX(380, 740))
            glow(f, X, Y, 150, (255, 236, 170), .75 * pill + .15 * math.sin(T * 5))
            sparkles(f, T, 14, 4, (X - 180, Y - 180, X + 180, Y + 180), 40, size=(5, 11))
        return f
    return seq(t, mk(shots_at, [A, B], d))

# ---------- 5 嫦娥吃仙丹飛上月亮 ----------
def scene5(t, d, p):
    shots_at = [0, p[1] - .2, p[3] - .2]
    eat = p[1] + 1.4
    def A(tt, dd):
        f = shot('s5a', tt, dd, z0=1.0, z1=1.07, c0=(.5, .5), c1=(.5, .46), bob=5)
        glow(f, 700, 1210, 90, (255, 232, 160), .8 + .15 * math.sin(tt * 4))
        glow(f, 700, 1210, 26, (255, 250, 225), 1)
        return f
    def B(tt, dd):
        T = tt + shots_at[1]
        f = shot('s5b', tt, dd, z0=1.0, z1=1.1, c0=(.5, .5), c1=PX(500, 620), bob=5)
        if T < eat:
            X, Y, _ = to_frame(*PX(500, 700), 's5b', tt, dd, z0=1.0, z1=1.1, c0=(.5, .5), c1=PX(500, 620))
            glow(f, X, Y, 80, (255, 232, 160), .8)
        X, Y, _ = to_frame(*PX(500, 600), 's5b', tt, dd, z0=1.0, z1=1.1, c0=(.5, .5), c1=PX(500, 620))
        burst(f, X, Y, (T - eat) / .7, 220)
        burst(f, X, Y, (T - p[2]) / .9, 320, 16)
        return f
    def C(tt, dd):
        u = ease(tt / dd)
        f = shot('s5c', tt, dd, z0=1.0, z1=1.04, c0=(.5, .56), c1=(.5, .48), bob=12, lift=260)
        glow(f, 460, 470 + 60 * u, 360, (255, 244, 215), .35 + .1 * math.sin(tt * 2))
        sparkles(f, tt, 50, 12, (250, 700 - 260 * u, 750, 1500), -140, col=(220, 205, 255), size=(5, 12))
        return f
    return seq(t, mk(shots_at, [A, B, C], d))

# ---------- 6 賞月吃月餅 ----------
def scene6(t, d, p):
    shots_at = [0, p[4] - .2]
    def A(tt, dd):
        f = shot('s6a', tt, dd, z0=1.06, z1=1.0, c0=(.5, .47), c1=(.5, .5), bob=6)
        sparkles(f, tt, 30, 21, (0, 150, W, 900), 20, size=(4, 9))
        return f
    def B(tt, dd):
        T = tt + shots_at[1]
        f = shot('s6c', tt, dd, z0=1.0, z1=1.08, c0=(.5, .5), c1=(.5, .46), bob=8)
        glow(f, 480, 560, 470, (255, 240, 205), .45 + .08 * math.sin(tt * 2))
        sparkles(f, tt, 40, 31, (0, 150, W, 1500), 30, size=(4, 10))
        tint(f, (255, 246, 238), seg(T, d - 1.0, d))
        return f
    return seq(t, mk(shots_at, [A, B], d))

SCENES = [scene1, scene2, scene3, scene4, scene5, scene6]

if __name__ == '__main__':
    audio = None
    tr = np.zeros(int(sum(D) * sr) + sr); t0 = 0
    for c, d in zip(clips, D):
        s = int((t0 + PRE) * sr); tr[s:s + len(c)] += c; t0 += d
    audio = out + '.wav'; sf.write(audio, tr[:int(sum(D) * sr)], sr)
    wr = Writer(out, None if ONLY else audio)
    prev = None
    for si, d in enumerate(D[:len(SCENES)]):
        prev_last = prev
        if ONLY and si + 1 != ONLY:
            continue
        n = int(round(d * FPS)); stp = 3 if FAST else 1
        for k in range(0, n, stp):
            t = k / FPS
            im = SCENES[si](t, d, P[si]).convert('RGB')
            if prev_last is not None and t < .5:
                im = Image.blend(prev_last, im, ease(t / .5))
            prev = im
            for _ in range(min(stp, n - k)):
                wr.write(im)
        print('scene', si + 1, 'ok', flush=True)
    wr.close(); os.remove(audio); print('done', out)
