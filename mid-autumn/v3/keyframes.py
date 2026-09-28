# 截每幕關鍵影格拼成一張檢查圖
import sys, io, os
from PIL import Image
from playwright.sync_api import sync_playwright
D = {2: 8.9, 3: 12.0, 4: 8.7, 5: 9.7, 6: 11.0}
U = [0.1, 0.3, 0.5, 0.7, 0.95]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    pg.goto('file://' + os.path.abspath('anim.html'))
    sheet = Image.new('RGB', (len(U) * 270, len(D) * 480))
    for r, (i, d) in enumerate(D.items()):
        for c, u in enumerate(U):
            pg.evaluate(f'renderScene({i},{u * d},{d})')
            im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB').resize((270, 480))
            sheet.paste(im, (c * 270, r * 480))
    sheet.save(sys.argv[1], quality=88); b.close()
