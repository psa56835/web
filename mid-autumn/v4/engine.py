# 動態繪本合成引擎：鏡頭推移 + 角色分層視差（定格 12fps）+ 光效粒子 + 絲滑轉場
import math, random, subprocess, numpy as np, cv2
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1080, 1920, 30
SAFE = (90, 250, 900, 1420)  # 直式短影音安全區：主體放這裡面


def ease(t):
    t = min(max(t, 0), 1); return t * t * (3 - 2 * t)


def seg(t, a, b):
    return min(max((t - a) / (b - a), 0), 1)


def step12(t):  # 定格動畫節奏：角色動作每秒 12 格
    return math.floor(t * 12) / 12


@lru_cache(None)
def plate(path, sep=True):
    """讀圖並放大到覆蓋 1080x1920（多留 12% 給鏡頭），可選擇把角色拆成前景層"""
    im = Image.open(path).convert('RGB')
    s = max(W / im.width, H / im.height) * 1.12
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    if not sep:
        return im.convert('RGBA'), None
    from rembg import remove, new_session
    fg = remove(im, session=new_session('birefnet-general-lite'), post_process_mask=True)
    m = np.array(fg.getchannel('A'))
    hole = cv2.dilate((m > 30).astype(np.uint8) * 255, np.ones((31, 31), np.uint8))
    bg = Image.fromarray(cv2.inpaint(np.array(im), hole, 11, cv2.INPAINT_TELEA))
    return bg.convert('RGBA'), fg


def view(img, z, cx, cy):
    """以 (cx,cy)（圖內比例座標）為中心、放大 z 倍裁出 1080x1920"""
    cw, ch = W / z, H / z  # 圖已放大到比畫面大 12%，z=1 時裁 1080x1920 原尺寸
    l = min(max(cx * img.width - cw / 2, 0), img.width - cw)
    t = min(max(cy * img.height - ch / 2, 0), img.height - ch)
    return img.resize((W, H), Image.BICUBIC, box=(l, t, l + cw, t + ch)), (l, t, cw / W)


def glow(frame, x, y, r, col, a):
    if a <= 0:
        return
    R = int(r * 1.6)
    lay = Image.new('RGBA', (2 * R, 2 * R), col + (0,))
    ImageDraw.Draw(lay).ellipse((R - r * .6, R - r * .6, R + r * .6, R + r * .6), fill=col + (int(255 * min(a, 1)),))
    lay = lay.filter(ImageFilter.GaussianBlur(r * .3))
    base = Image.new('RGBA', frame.size, (0, 0, 0, 0)); base.paste(lay, (int(x - R), int(y - R)))
    frame.alpha_composite(base)


def star(d, x, y, r, col=(255, 244, 214), a=230):
    k = r * .3
    d.polygon([(x, y - r), (x + k, y - k), (x + r, y), (x + k, y + k), (x, y + r), (x - k, y + k), (x - r, y), (x - k, y - k)], fill=col + (int(a),))


def sparkles(frame, t, n=40, seed=0, area=(0, 0, W, H), rise=60, col=(255, 244, 214), size=(4, 11)):
    lay = Image.new('RGBA', frame.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); r = random.Random(seed)
    x0, y0, x1, y1 = area
    for i in range(n):
        x, y, s, ph = r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(*size), r.uniform(0, 6.3)
        y = y0 + (y - y0 - t * rise) % (y1 - y0)
        star(d, x, y, s * (0.6 + 0.4 * abs(math.sin(t * 2 + ph))), col, 220 * abs(math.sin(t * 1.7 + ph)))
    frame.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.6)))


def burst(frame, x, y, k, R=200, n=12):
    if not 0 <= k < 1:
        return
    glow(frame, x, y, 120 + 200 * k, (255, 246, 220), 1 - k)
    lay = Image.new('RGBA', frame.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for q in range(n):
        a = q / n * 2 * math.pi
        star(d, x + math.cos(a) * R * k, y + math.sin(a) * R * k, 30 * (1 - k) + 6, (255, 241, 200) if q % 2 else (205, 190, 240), 255 * (1 - k))
    frame.alpha_composite(lay)


def tint(frame, col, a):
    if a > 0:
        frame.alpha_composite(Image.new('RGBA', frame.size, col + (int(255 * min(a, 1)),)))


def vignette(frame, a=0.35):
    v = VIG.copy(); v.putalpha(VIG.getchannel('A').point(lambda x: int(x * a))); frame.alpha_composite(v)


_y, _x = np.mgrid[0:H, 0:W]
_d = np.sqrt(((_x - W / 2) / (W * .75)) ** 2 + ((_y - H * .45) / (H * .75)) ** 2)
VIG = Image.fromarray((np.clip((_d - .45) / .6, 0, 1) * 255).astype(np.uint8)); VIG = Image.merge('RGBA', [Image.new('L', (W, H), 30)] * 3 + [VIG])


class Writer:
    def __init__(self, out, audio=None):
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
        if audio:
            cmd += ['-i', audio, '-c:a', 'aac', '-b:a', '192k', '-shortest']
        cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def write(self, im):
        self.p.stdin.write(im.convert('RGB').tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()
