# 紙雕風格工具：撕紙邊、紙紋、白邊、投影
import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 1080, 1920
# 9:16 短影音安全區（避開上方帳號列、右側按鈕、下方文案區）
SAFE = (90, 250, 900, 1420)

_rng = np.random.default_rng(3)
GRAIN = Image.fromarray((_rng.normal(0, 1, (H // 2, W // 2)) * 9 + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(0.8))
FIBER = Image.fromarray((_rng.normal(0, 1, (H // 8, W // 8)) * 14 + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)


def paper_tex(im, k=1.0):
    """疊紙纖維與顆粒"""
    a = np.asarray(im.convert('RGB'), np.float32)
    g = (np.asarray(GRAIN, np.float32) - 128) + (np.asarray(FIBER, np.float32) - 128) * 0.6
    return Image.fromarray((a + g[..., None] * 0.55 * k).clip(0, 255).astype(np.uint8))


def torn(points, amp=6, seed=0):
    """把折線加上撕紙鋸齒"""
    r = random.Random(seed); out = []
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 9))
        for i in range(n):
            u = i / n
            out.append((x0 + (x1 - x0) * u + r.uniform(-amp, amp) * .5, y0 + (y1 - y0) * u + r.uniform(-amp, amp)))
    return out


def cutout(size, draw_fn, col, border=9, shadow=(10, 16, 14, 0.35), tex=1.0):
    """畫一塊紙片：白色撕邊 + 投影 + 紙紋。回傳 RGBA"""
    m = Image.new('L', size, 0); draw_fn(ImageDraw.Draw(m))
    return decorate(Image.new('RGB', size, col), m, border, shadow, tex)


def decorate(rgb, mask, border=9, shadow=(10, 16, 14, 0.35), tex=1.0):
    size = mask.size
    edge = mask.filter(ImageFilter.MaxFilter(border * 2 + 1)) if border else mask
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    if shadow:
        dx, dy, bl, a = shadow
        sh = Image.new('RGBA', size, (40, 24, 30, 0)); sh.putalpha(edge.point(lambda v: int(v * a)).filter(ImageFilter.GaussianBlur(bl)))
        out.alpha_composite(sh, (dx, dy)) if dx >= 0 and dy >= 0 else out.alpha_composite(sh)
    if border:
        wb = Image.new('RGBA', size, (253, 248, 238, 0)); wb.putalpha(edge); out.alpha_composite(wb)
    body = paper_tex(rgb, tex).convert('RGBA') if rgb.size == (W, H) else rgb.convert('RGBA')
    body.putalpha(mask); out.alpha_composite(body)
    return out


def sticker(img, border=12, shadow=(12, 18, 16, 0.4)):
    """把去背角色做成紙偶：白邊 + 投影"""
    pad = border * 2 + 40
    base = Image.new('RGBA', (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0)); base.paste(img, (pad, pad), img)
    a = base.getchannel('A').point(lambda v: 255 if v > 100 else 0)
    edge = a.filter(ImageFilter.MaxFilter(border * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new('RGBA', base.size, (0, 0, 0, 0))
    dx, dy, bl, al = shadow
    sh = Image.new('RGBA', base.size, (40, 24, 30, 0)); sh.putalpha(edge.point(lambda v: int(v * al)).filter(ImageFilter.GaussianBlur(bl)))
    out.alpha_composite(sh, (dx, dy))
    wb = Image.new('RGBA', base.size, (253, 248, 238, 0)); wb.putalpha(edge); out.alpha_composite(wb)
    out.alpha_composite(base)
    return out


def vgrad(c0, c1, h=H, w=W):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t
    return Image.fromarray(np.repeat(a, w, 1).astype(np.uint8))


def hex2(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
