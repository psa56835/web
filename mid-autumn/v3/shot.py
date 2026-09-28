import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': int(sys.argv[3]), 'height': int(sys.argv[4])})
    pg.goto('file://' + __import__('os').path.abspath(sys.argv[1])); pg.wait_for_timeout(300)
    pg.screenshot(path=sys.argv[2]); b.close()
