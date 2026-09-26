# 素材前處理：背景放大+調色到設定圖色票、角色去背裁邊
# python3 prep.py bg raw/bg2_11.png bg2      -> assets/bg2.png
# python3 prep.py ch raw/sun_21.png sun      -> assets/sun.png
import sys, os, numpy as np
from PIL import Image, ImageEnhance, ImageFilter

W, H = 1080, 1920
CREAM = np.array([0xFF, 0xF6, 0xEE], np.float32)
os.makedirs('assets', exist_ok=True)


def grade(im, sat=0.82, wash=0.12):
    im = ImageEnhance.Color(im).enhance(sat)
    a = np.asarray(im.convert('RGB'), np.float32)
    a = a * (1 - wash) + CREAM * wash  # 往奶油色靠，貼近色票
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def bg(src, name, sat=0.82, wash=0.12):
    im = Image.open(src).convert('RGB')
    s = max(W / im.width, H / im.height) * 1.12  # 多留 12% 給推移運鏡
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(2, 60, 2))
    grade(im, sat, wash).save(f'assets/{name}.png')


def ch(src, name, model='isnet-anime'):
    from rembg import remove, new_session
    im = Image.open(src).convert('RGB')
    out = remove(im, session=new_session(model), post_process_mask=True)
    out = out.crop(out.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox())
    rgb = grade(out.convert('RGB'), 0.9, 0.05)
    rgb.putalpha(out.getchannel('A'))
    rgb.save(f'assets/{name}.png')


if __name__ == '__main__':
    {'bg': bg, 'ch': ch}[sys.argv[1]](*sys.argv[2:])
