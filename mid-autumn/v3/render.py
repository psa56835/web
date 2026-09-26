# v3 主渲染：第 1 幕用分鏡圖慢推，2～6 幕由 anim.html 逐格截圖，依語音長度排時間軸
# python3 render.py out.mp4 [vo資料夾] [--fast]
import io, os, sys, json, math, subprocess, numpy as np, soundfile as sf
from PIL import Image, ImageFilter, ImageDraw
from playwright.sync_api import sync_playwright

W, H, FPS = 1080, 1920, 30
PRE, POST = 0.35, 0.5
DEFAULT = [5.2, 8.1, 11.2, 7.9, 8.9, 9.4]  # 沒有語音時的暫定每句長度
out = sys.argv[1]
vo = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
step = 3 if '--fast' in sys.argv else 1

clips, sr = [], 24000
for i in range(6):
    p = f'{vo}/l{i + 1}.wav' if vo else None
    if p and os.path.exists(p):
        y, sr = sf.read(p); clips.append(y if y.ndim == 1 else y.mean(1))
    else:
        clips.append(None)
D = [(len(c) / sr if c is not None else DEFAULT[i]) + PRE + POST for i, c in enumerate(clips)]
D[-1] += 0.8
cues = json.load(open('cues.json')) if os.path.exists('cues.json') else {}
print('段長', [round(d, 2) for d in D], '總長', round(sum(D), 2))

# 第 1 幕：分鏡圖放大到 1080x1920，慢推 + 月光/檯燈柔光呼吸
SRC = Image.open('../src/ref/scene1.png').convert('RGB')
BASE = SRC.resize((W, round(SRC.height * W / SRC.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 50, 2))
BASE = BASE.resize((W, H), Image.LANCZOS) if BASE.height != H else BASE


def glow_layer(cx, cy, r, col):
    g = Image.new('RGBA', (W, H), col + (0,))
    ImageDraw.Draw(g).ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,))
    return g.filter(ImageFilter.GaussianBlur(r * 0.5))


MOON = glow_layer(196, 184, 150, (255, 244, 220))   # 窗外月亮（1080 寬座標）
LAMP = glow_layer(985, 590, 120, (255, 214, 150))   # 兔子燈


def scene1(t, d):
    im = BASE.convert('RGBA')
    for lay, a in ((MOON, 0.22 + 0.12 * math.sin(t * 1.6)), (LAMP, 0.25 + 0.12 * math.sin(t * 2.1 + 1))):
        l = lay.copy(); l.putalpha(lay.getchannel('A').point(lambda v: int(v * a))); im.alpha_composite(l)
    z = 1.0 + 0.07 * (t / d)
    cw, ch = W / z, H / z
    l, tp = (W - cw) * 0.45, (H - ch) * 0.45
    return im.resize((W, H), Image.BICUBIC, box=(l, tp, l + cw, tp + ch)).convert('RGB')


audio = None
if vo:
    tr = np.zeros(int(sum(D) * sr) + sr); t0 = 0
    for c, d in zip(clips, D):
        if c is not None:
            s = int((t0 + PRE) * sr); tr[s:s + len(c)] += c
        t0 += d
    audio = out + '.wav'; sf.write(audio, tr[:int(sum(D) * sr)], sr)

cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
if audio:
    cmd += ['-i', audio, '-c:a', 'aac', '-b:a', '192k', '-shortest']
cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': W, 'height': H}); pg.goto('file://' + os.path.abspath('anim.html'))
    for si, d in enumerate(D):
        n = int(round(d * FPS)); cue = json.dumps(cues.get(str(si + 1), {}))
        for k in range(0, n, step):
            t = k / FPS
            if si == 0:
                im = scene1(t, d)
            else:
                pg.evaluate(f'renderScene({si + 1},{t},{d},{cue})')
                im = Image.open(io.BytesIO(pg.screenshot(type='jpeg', quality=95))).convert('RGB')
            buf = im.tobytes()
            for _ in range(min(step, n - k)):
                ff.stdin.write(buf)
        print('scene', si + 1, 'ok', flush=True)
    b.close()
ff.stdin.close(); ff.wait()
if audio:
    os.remove(audio)
print('done', out)
