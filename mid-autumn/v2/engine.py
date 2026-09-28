# 2D 合成小引擎：圖層貼上（縮放/旋轉/透明度）、粒子、緩動，逐格輸出給 ffmpeg
import math, random, subprocess, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1080, 1920, 30


@lru_cache(None)
def load(name):
    return Image.open(f'assets/{name}.png').convert('RGBA')


@lru_cache(512)
def _xf(name, h, rot, flip):
    im = load(name)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    s = h / im.height
    im = im.resize((max(1, round(im.width * s)), max(1, h)), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    return im


def put(canvas, name, cx, cy, h, rot=0.0, alpha=1.0, flip=False, anchor='c'):
    """把素材貼到 canvas，h=顯示高度(px)，anchor c=中心 b=底部中心"""
    im = _xf(name, int(round(h)), round(rot, 1), flip)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * max(0, alpha))))
    x = int(cx - im.width / 2)
    y = int(cy - im.height / 2) if anchor == 'c' else int(cy - im.height)
    canvas.alpha_composite(im, (x, y)) if 0 <= x and 0 <= y and x + im.width <= canvas.width and y + im.height <= canvas.height \
        else canvas.paste(im, (x, y), im)


def cam(name, t, z0=1.0, z1=1.05, x0=0.5, y0=0.5, x1=0.5, y1=0.5):
    """背景推移：縮放 z、焦點 (x,y) 以比例表示，t∈[0,1]"""
    bg = load(name)
    z = z0 + (z1 - z0) * t
    fx, fy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
    # 以背景為基準裁一個 9:16 視窗
    base = min(bg.width / W, bg.height / H)
    cw, ch = W * base / z, H * base / z
    l = min(max(fx * bg.width - cw / 2, 0), bg.width - cw)
    tp = min(max(fy * bg.height - ch / 2, 0), bg.height - ch)
    return bg.resize((W, H), Image.BILINEAR, box=(l, tp, l + cw, tp + ch))


def ease(t):
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)


def back(t):  # 彈出感
    t = min(max(t, 0), 1); c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def seg(t, a, b):
    return min(max((t - a) / (b - a), 0), 1)


def sparkle(d, x, y, r, col=(255, 246, 200), a=255):
    """四角星"""
    k = r * 0.28
    pts = [(x, y - r), (x + k, y - k), (x + r, y), (x + k, y + k), (x, y + r), (x - k, y + k), (x - r, y), (x - k, y - k)]
    d.polygon(pts, fill=col + (a,))


def heart(d, x, y, r, col=(217, 168, 177), a=255):
    d.ellipse((x - r, y - r * .8, x, y + r * .2), fill=col + (a,))
    d.ellipse((x, y - r * .8, x + r, y + r * .2), fill=col + (a,))
    d.polygon([(x - r * .97, y - r * .1), (x + r * .97, y - r * .1), (x, y + r)], fill=col + (a,))


def overlay(canvas, draw_fn, blur=0):
    lay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    if blur:
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(lay)


def glow(canvas, x, y, r, col, a):
    R = int(r * 1.5)
    lay = Image.new('RGBA', (2 * R, 2 * R), col + (0,))
    ImageDraw.Draw(lay).ellipse((R - r * .6, R - r * .6, R + r * .6, R + r * .6), fill=col + (int(a),))
    lay = lay.filter(ImageFilter.GaussianBlur(r * .22))
    base = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); base.paste(lay, (int(x - R), int(y - R)))
    canvas.alpha_composite(base)


class Writer:
    def __init__(self, out, audio=None):
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
        if audio:
            cmd += ['-i', audio, '-c:a', 'aac', '-b:a', '192k', '-shortest']
        cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def write(self, im):
        self.p.stdin.write(im.convert('RGB').tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()
