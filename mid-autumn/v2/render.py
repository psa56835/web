# 主渲染：依每句語音長度排時間軸，硬切換場，輸出 1080x1920 mp4
# python3 render.py out.mp4 [vo資料夾] [--fast]
import os, sys, json, numpy as np, soundfile as sf
from engine import *
import s1, scenes

FRAMES = [s1.frame, scenes.s2, scenes.s3, scenes.s4, scenes.s5, scenes.s6]
PRE, POST = 0.35, 0.45           # 每段語音前後留白
MIN_D = [5, 7, 10, 7, 9, 9]      # 無語音時的預設段長
SR = 22050

out = sys.argv[1]
vo = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
step = 3 if '--fast' in sys.argv else 1

clips = []
for i in range(6):
    p = f'{vo}/l{i + 1}.wav' if vo else None
    clips.append(sf.read(p)[0] if p and os.path.exists(p) else None)
D = [(len(c) / SR + PRE + POST) if c is not None else MIN_D[i] for i, c in enumerate(clips)]
D[-1] += 0.8  # 結尾淡出
print('段長', [round(d, 2) for d in D], '總長', round(sum(D), 2))

audio = None
if vo:
    tr = np.zeros(int(sum(D) * SR) + SR)
    t0 = 0
    for c, d in zip(clips, D):
        if c is not None:
            s = int((t0 + PRE) * SR); tr[s:s + len(c)] += c
        t0 += d
    audio = out + '.wav'; sf.write(audio, tr[:int(sum(D) * SR)], SR)

wr = Writer(out, audio)
for fn, d in zip(FRAMES, D):
    n = int(round(d * FPS))
    for k in range(0, n, step):
        im = fn(k / FPS, d)
        for _ in range(min(step, n - k)):
            wr.write(im)
wr.close()
if audio:
    os.remove(audio)
print('done', out)
