# 測試：單幕 2.5D 動態（角色分層漂浮 + 背景視差 + 光效粒子）
import math, random, subprocess, numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw
from rembg import remove, new_session
W, H, FPS, D = 1080, 1920, 30, 5.0
src = Image.open('raw/d5_301.png').convert('RGB')
s = max(W / src.width, H / src.height) * 1.1
src = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
fg = remove(src, session=new_session('birefnet-general-lite'), post_process_mask=True)
m = np.array(fg.getchannel('A'))
hole = cv2.dilate((m > 30).astype(np.uint8) * 255, np.ones((25, 25), np.uint8))
bg = Image.fromarray(cv2.inpaint(np.array(src), hole, 9, cv2.INPAINT_TELEA)).filter(ImageFilter.GaussianBlur(1.2))
glowL = Image.new('RGBA', src.size, (255, 244, 220, 0)); ImageDraw.Draw(glowL).ellipse((150, 0, src.width - 150, 750), fill=(255, 244, 220, 255)); glowL = glowL.filter(ImageFilter.GaussianBlur(120))
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', 'test_clip.mp4'], stdin=subprocess.PIPE)
P = [(random.uniform(0, W), random.uniform(0, H), random.uniform(3, 9), random.uniform(0, 6)) for _ in range(60)]
for k in range(int(D * FPS)):
    t = k / FPS; u = t / D; e = u * u * (3 - 2 * u)
    cx, cy = src.width / 2, src.height / 2
    # 背景：慢推 + 輕微往下（鏡頭上仰）
    zb = 1.0 + 0.04 * e
    f = bg.resize((round(src.width * zb), round(src.height * zb)), Image.BICUBIC).convert('RGBA')
    ox, oy = (f.width - W) / 2, (f.height - H) / 2 - 30 * e
    frame = f.crop((ox, oy, ox + W, oy + H))
    g = glowL.crop((ox, oy, ox + W, oy + H)); a = 0.18 + 0.10 * math.sin(t * 2)
    g.putalpha(g.getchannel('A').point(lambda v: int(v * a))); frame.alpha_composite(g)
    # 角色：往上飄 + 左右輕晃，比背景推得多（視差）
    zf = 1.0 + 0.09 * e
    c = fg.resize((round(fg.width * zf), round(fg.height * zf)), Image.BICUBIC).rotate(math.sin(t * 1.6) * 1.8, Image.BICUBIC)
    frame.alpha_composite(c, (int(W / 2 - c.width / 2 + math.sin(t * 1.3) * 10), int(H / 2 - c.height / 2 - 120 * e - 10 * math.sin(t * 2.2))))
    # 星光粒子往上飄
    d = ImageDraw.Draw(frame)
    for x, y0, r, ph in P:
        y = (y0 - t * 90) % H; al = int(200 * abs(math.sin(t * 2 + ph)))
        d.polygon([(x, y - r), (x + r * .3, y - r * .3), (x + r, y), (x + r * .3, y + r * .3), (x, y + r), (x - r * .3, y + r * .3), (x - r, y), (x - r * .3, y - r * .3)], fill=(255, 240, 210, al))
    ff.stdin.write(frame.convert('RGB').tobytes())
ff.stdin.close(); ff.wait(); print('ok')
