# 風格測試：嫦娥飛上月亮（紙雕 + 分鏡圖風角色 + 安全區）
import math
from PIL import Image, ImageDraw
from paper import *

bg = paper_tex(vgrad(hex2('#2F3558'), hex2('#8F86B0')), 1.2).convert('RGBA')
# 星星紙片
for i in range(22):
    r = random.Random(i); x, y, s = r.uniform(60, 1020), r.uniform(80, 1100), r.uniform(10, 22)
    pts = [(x + math.cos(a * math.pi / 5 - math.pi / 2) * (s if a % 2 == 0 else s * .45), y + math.sin(a * math.pi / 5 - math.pi / 2) * (s if a % 2 == 0 else s * .45)) for a in range(10)]
    bg.alpha_composite(cutout((W, H), lambda d, p=pts: d.polygon(p, fill=255), hex2('#FFE9B8'), border=3, shadow=(3, 5, 4, .3)))
# 月亮（紙雕圓 + 光暈）
glow = Image.new('RGBA', (W, H), (255, 240, 205, 0)); ImageDraw.Draw(glow).ellipse((540 - 330, 560 - 330, 540 + 330, 560 + 330), fill=(255, 240, 205, 120))
bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70)))
bg.alpha_composite(cutout((W, H), lambda d: d.polygon(torn([(540 + 230 * math.cos(a / 40 * 2 * math.pi), 560 + 230 * math.sin(a / 40 * 2 * math.pi)) for a in range(40)], 4, 1), fill=255), hex2('#FCEBCB'), border=10))
bg.alpha_composite(cutout((W, H), lambda d: [d.ellipse(b, fill=255) for b in ((455, 470, 525, 530), (590, 610, 640, 650), (500, 640, 540, 672))], hex2('#EED6B2'), border=0, shadow=None))
# 雲
def cloud(d, x, y, s):
    for cx, cy, r in ((0, 0, 70), (-80, 20, 55), (80, 20, 55), (-40, -40, 60), (40, -35, 65)):
        d.ellipse((x + (cx - r) * s, y + (cy - r) * s, x + (cx + r) * s, y + (cy + r) * s), fill=255)
    d.rectangle((x - 130 * s, y + 10 * s, x + 130 * s, y + 70 * s), fill=255)
bg.alpha_composite(cutout((W, H), lambda d: (cloud(d, 200, 900, 1.2), cloud(880, 760, 1.0) if False else cloud(d, 880, 760, 1.0)), hex2('#A69CC6'), border=7))
# 屋頂與山丘（撕紙層）
bg.alpha_composite(cutout((W, H), lambda d: d.polygon(torn([(-20, 1500), (200, 1380), (430, 1440), (650, 1350), (880, 1420), (1100, 1370), (1100, 1950), (-20, 1950)], 7, 2), fill=255), hex2('#6E6390'), border=8))
bg.alpha_composite(cutout((W, H), lambda d: d.polygon(torn([(-20, 1600), (300, 1540), (620, 1590), (1100, 1520), (1100, 1950), (-20, 1950)], 7, 3), fill=255), hex2('#4A3F5E'), border=8))
# 嫦娥紙偶（置中偏上，在安全區內）
ch = Image.open('change.png'); ch = ch.resize((int(ch.width * 640 / ch.height), 640), Image.LANCZOS)
st = sticker(ch).rotate(-4, Image.BICUBIC, expand=True)
bg.alpha_composite(st, (540 - st.width // 2, 1000 - st.height // 2))
# 星光拖尾
d = ImageDraw.Draw(bg)
for q in range(12):
    x, y = 540 + math.sin(q) * 60, 1330 + q * 34
    s = 16 - q
    d.polygon([(x, y - s), (x + s * .3, y - s * .3), (x + s, y), (x + s * .3, y + s * .3), (x, y + s), (x - s * .3, y + s * .3), (x - s, y), (x - s * .3, y - s * .3)], fill=(255, 240, 200, 230))
bg.convert('RGB').save('test_s5.png')
# 安全區示意
g = bg.copy(); d = ImageDraw.Draw(g)
d.rectangle((0, 0, W, SAFE[1]), fill=(255, 0, 0, 60)); d.rectangle((0, SAFE[3], W, H), fill=(255, 0, 0, 60)); d.rectangle((SAFE[2], SAFE[1], W, SAFE[3]), fill=(255, 0, 0, 60))
d.rectangle(SAFE, outline=(255, 80, 80), width=4)
g.convert('RGB').save('test_s5_safe.png')
