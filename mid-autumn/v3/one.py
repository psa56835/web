import sys, os
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': 1080, 'height': 1920}); pg.goto('file://' + os.path.abspath('anim.html'))
    pg.evaluate(f'renderScene({sys.argv[1]},{sys.argv[2]},{sys.argv[3]})'); pg.screenshot(path=sys.argv[4]); b.close()
