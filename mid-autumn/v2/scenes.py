# 第 2～6 段故事動畫，每段 frame(t, d)：t=段內秒數, d=段長
import numpy as np
from PIL import Image, ImageDraw
from engine import *

R = random.Random(7)


def zoom_out(f, t, d, z0=1.06, fy=0.5):
    z = z0 + (1 - z0) * ease(t / d)
    cw, ch = W / z, H / z
    return f.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) * fy, (W + cw) / 2, (H - ch) * fy + ch))


def tint(f, col, a):
    if a > 0:
        f.alpha_composite(Image.new('RGBA', f.size, col + (int(a),)))


# ---------- 2. 十個太陽 ----------
SUNS = [(150, 170), (420, 110), (700, 150), (950, 200), (280, 360), (560, 330), (830, 400), (130, 560), (430, 560), (720, 610)]


def s2(t, d):
    f = cam('bg2', t / d, 1.0, 1.0, 0.5, 0.55, 0.5, 0.55)
    tint(f, (255, 170, 90), 40 + 25 * math.sin(t * 3))  # 熱到發燙
    for i, (x, y) in enumerate(SUNS):
        s = back(seg(t, 0.12 * i, 0.12 * i + 0.5))
        if s > 0:
            glow(f, x, y, 170, (255, 220, 120), 110)
            put(f, 'sun', x, y + math.sin(t * 2.5 + i) * 10, 190 * s, rot=math.sin(t * 1.7 + i * 2) * 10)
    sq = 1 + 0.03 * math.sin(t * 5)
    put(f, 'hot', 540, 1880, 760 * sq, anchor='b')

    def drops(dr):  # 汗滴
        for k in range(8):
            u = (t * 0.9 + k / 8) % 1
            x = 300 + (k * 97) % 480
            y = 1250 + u * 260
            a = int(220 * math.sin(u * math.pi))
            dr.ellipse((x - 9, y - 14, x + 9, y + 14), fill=(185, 205, 230, a))
    overlay(f, drops)
    return f


# ---------- 3. 后羿射日 ----------
VOLLEY = [(0.395, (0, 3, 7)), (0.452, (1, 5, 8)), (0.508, (2, 4, 9))]  # (時間比例, 射中的太陽)，留下 6 號
KEEP = 6
SUNS3 = [(150, 200), (410, 130), (680, 170), (940, 230), (270, 390), (560, 300), (820, 420), (140, 590), (430, 600), (700, 640)]
BOW = (700, 1060)  # 弓的位置（畫面座標）


def s3(t, d):
    u = t / d
    f = cam('bg3', u, 1.08, 1.0, 0.5, 0.35, 0.5, 0.5)
    hit = {}
    for tr, ids in VOLLEY:
        for j, i in enumerate(ids):
            hit[i] = tr * d + 0.12 * j
    for i, (x, y) in enumerate(SUNS3):
        if i == KEEP:
            # 最後一個太陽：移到中間，上班下班地上下跳
            k = ease(seg(u, 0.62, 0.78))
            bx, by = x + (540 - x) * k, y + (330 - y) * k
            by += 140 * math.sin(max(0, u - 0.8) / 0.2 * 2 * math.pi) * seg(u, 0.8, 0.84)
            glow(f, bx, by, 190 + 60 * k, (255, 225, 130), 120)
            put(f, 'sun', bx, by + math.sin(t * 2.5) * 8, 200 + 90 * k, rot=math.sin(t * 1.7) * 8)
            continue
        th = hit[i]
        if t < th:
            glow(f, x, y, 160, (255, 220, 120), 100)
            put(f, 'sun', x, y + math.sin(t * 2.5 + i) * 8, 180, rot=math.sin(t * 1.7 + i * 2) * 10)
        elif t < th + 0.9:
            k = (t - th) / 0.9  # 被射中：閃一下、轉著掉下去
            put(f, 'sun', x + 60 * k, y + 700 * k * k, 180 * (1 - 0.5 * k), rot=200 * k, alpha=1 - k)
    # 箭
    def arrows(dr):
        for tr, ids in VOLLEY:
            for j, i in enumerate(ids):
                th = tr * d + 0.12 * j; t0 = th - 0.35
                if t0 <= t < th:
                    k = (t - t0) / 0.35
                    tx, ty = SUNS3[i]
                    x = BOW[0] + (tx - BOW[0]) * k; y = BOW[1] + (ty - BOW[1]) * k
                    ang = math.atan2(ty - BOW[1], tx - BOW[0])
                    dx, dy = math.cos(ang) * 150, math.sin(ang) * 150
                    dr.line((x - dx * 3, y - dy * 3, x - dx * .5, y - dy * .5), fill=(255, 246, 200, 150), width=26)  # 殘影
                    dr.line((x - dx * 2, y - dy * 2, x - dx * .5, y - dy * .5), fill=(255, 255, 240, 200), width=12)
                    dr.line((x - dx, y - dy, x, y), fill=(140, 107, 87, 255), width=14)
                    dr.polygon([(x + dx * .3, y + dy * .3), (x - dy * .18, y + dx * .18), (x + dy * .18, y - dx * .18)], fill=(217, 168, 177, 255))
                if th <= t < th + 0.5:  # 命中火花
                    k = (t - th) / 0.5; tx, ty = SUNS3[i]
                    for q in range(8):
                        a = q / 8 * 2 * math.pi
                        sparkle(dr, tx + math.cos(a) * 180 * k, ty + math.sin(a) * 180 * k, 40 * (1 - k) + 6, a=int(255 * (1 - k)))
    overlay(f, arrows)
    recoil = sum(max(0, 1 - abs(t - (tr * d + 0.12 * j - 0.35)) / 0.15) for tr, ids in VOLLEY for j in range(3))
    put(f, 'shoot', 470 + recoil * 12, 1920, 860, rot=14, flip=True, anchor='b')
    return f


# ---------- 4. 當國王、變兇、拿到仙丹 ----------
def s4(t, d):
    u = t / d
    f = cam('bg4', u, 1.0, 1.08, 0.5, 0.55, 0.5, 0.6)
    s = back(seg(u, 0.02, 0.18))
    angry = seg(u, 0.35, 0.5)
    shake = math.sin(t * 40) * 8 * angry * (1 - seg(u, 0.5, 0.6))
    tint(f, (120, 40, 50), 70 * angry)
    if s > 0:
        put(f, 'king', 540 + shake, 1780, 1000 * s, anchor='b')
    ca = seg(u, 0.25, 0.4)
    if ca < 1:  # 百姓歡呼，之後往下退場
        put(f, 'cheer', 540, 1940 + 700 * ease(ca) - abs(math.sin(t * 6)) * 25, 620, anchor='b')
    e = back(seg(u, 0.62, 0.78))
    if e > 0:
        ex, ey = 830, 1180 + math.sin(t * 3) * 20
        glow(f, ex, ey, 260, (255, 235, 150), 170 * e)
        put(f, 'elixir', ex, ey, 300 * e)

        def sp(dr):
            for q in range(6):
                a = t * 1.5 + q * 1.05
                sparkle(dr, ex + math.cos(a) * 190, ey + math.sin(a) * 150, 22 + 8 * math.sin(t * 6 + q), a=int(230 * e))
        overlay(f, sp)
    return f


# ---------- 5. 嫦娥吃仙丹飛上月亮 ----------
MOON5 = (780, 420)


def s5(t, d):
    u = t / d
    f = cam('bg5', ease(seg(u, 0.4, 0.95)), 1.12, 1.0, 0.5, 0.75, 0.5, 0.5)
    fly = seg(u, 0.45, 0.95)
    if u < 0.45:
        # 擔心 → 偷吃仙丹
        put(f, 'worry', 540, 1880 + math.sin(t * 2) * 6, 1000, anchor='b')
        e = 1 - seg(u, 0.3, 0.42)
        if e > 0:
            glow(f, 800 - 240 * seg(u, 0.3, 0.42), 1250, 200, (255, 235, 150), 150 * e)
            k = seg(u, 0.3, 0.42)
            put(f, 'elixir', 800 + (560 - 800) * k, 1250 - 60 * k, 180 * e)
    else:
        k = ease(fly)
        x = 540 + (MOON5[0] - 540) * k + math.sin(t * 2.2) * 40 * (1 - k)
        y = 1350 + (MOON5[1] + 60 - 1350) * k
        h = 900 * (1 - 0.72 * k)
        glow(f, x, y, h * 0.7, (255, 240, 200), 120)
        put(f, 'fly', x, y, h, rot=math.sin(t * 2) * 5)

        def trail(dr):
            for q in range(14):
                v = q / 14
                kk = ease(max(0, fly - v * 0.25))
                px = 540 + (MOON5[0] - 540) * kk + math.sin(t * 3 + q) * 60
                py = 1350 + (MOON5[1] + 60 - 1350) * kk + 250
                sparkle(dr, px, py, 18 * (1 - v) + 4, col=(205, 183, 233), a=int(220 * (1 - v)))
        overlay(f, trail)
    return f


# ---------- 6. 賞月吃月餅 ----------
MOON6 = (650, 400)


def s6(t, d):
    u = t / d
    f = cam('bg6', u, 1.06, 1.0, 0.5, 0.45, 0.5, 0.5)
    glow(f, MOON6[0], MOON6[1], 330, (255, 246, 220), 110 + 30 * math.sin(t * 2))
    put(f, 'cmoon', MOON6[0], MOON6[1] + math.sin(t * 1.8) * 12, 380 * back(seg(u, 0.35, 0.5)) + 1, alpha=0.95)
    for i, (x, y, h) in enumerate([(110, 260, 330), (980, 330, 300)]):
        put(f, 'lantern', x, y, h, rot=math.sin(t * 1.6 + i * 2) * 9)
    put(f, 'vmoon', 540, 1900, 780 * back(seg(u, 0.0, 0.12)) + 1, anchor='b')
    for i, (x, y) in enumerate([(105, 1840), (975, 1850)]):
        put(f, 'mooncake', x, y - abs(math.sin(t * 3 + i * 1.5)) * 30, 170, rot=math.sin(t * 2 + i) * 8)

    def st(dr):
        for q in range(12):
            r = random.Random(q)
            x, y = r.uniform(60, 1020), r.uniform(80, 900)
            sparkle(dr, x, y, 10 + 10 * abs(math.sin(t * 2 + q)), a=int(200 * abs(math.sin(t * 1.3 + q))))
    overlay(f, st)
    tint(f, (255, 246, 238), 255 * seg(t, d - 0.8, d))  # 結尾淡出到奶油色
    return f
