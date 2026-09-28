# 第一段：媽媽和熊寶窩在床上，被子當前景
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from engine import *

BG = cam('bed', 0, 1.0, 1.0)
# 被子上緣（量自 bed 背景），被子以下的背景當前景蓋住人物
EDGE = [(0, 1235), (200, 1225), (420, 1190), (640, 1200), (860, 1240), (1000, 1320), (1080, 1350)]
_m = Image.new('L', (W, H), 0)
ImageDraw.Draw(_m).polygon(EDGE + [(W, H), (0, H)], fill=255)
FG = BG.copy(); FG.putalpha(_m.filter(ImageFilter.GaussianBlur(6)))

HEARTS = [(random.Random(i).uniform(250, 850), random.Random(i + 50).uniform(0, 1), random.Random(i + 99).uniform(18, 34)) for i in range(7)]


def frame(t, d):
    """t=本段秒數, d=本段總長"""
    f = BG.copy()
    br = math.sin(t * 2.2)  # 呼吸晃動
    put(f, 'm2', 420, 1440 + br * 6, 900, rot=-7 + br * 1.2, anchor='b')
    put(f, 'k2', 700, 1360 - br * 5, 760, rot=6 - br * 1.5, anchor='b')
    f.alpha_composite(FG)

    def fx(dr):
        for x, ph, r in HEARTS:
            u = (t / 3.2 + ph) % 1
            heart(dr, x + math.sin(u * 6 + ph * 9) * 30, 700 - u * 520, r, a=int(230 * math.sin(u * math.pi)))
    overlay(f, fx)
    z = 1.0 + 0.06 * ease(t / d)  # 慢慢推近
    cw, ch = W / z, H / z
    return f.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) * 0.4, (W + cw) / 2, (H - ch) * 0.4 + ch))


if __name__ == '__main__':
    frame(1.0, 5).convert('RGB').resize((540, 960)).save('test/s1.jpg')
