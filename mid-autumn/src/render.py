import base64, subprocess, json, threading, http.server, functools, imageio_ffmpeg
from playwright.sync_api import sync_playwright
FF=imageio_ffmpeg.get_ffmpeg_exe(); PORT=8766
h=functools.partial(http.server.SimpleHTTPRequestHandler,directory='.'); h.log_message=lambda *a:None
srv=http.server.ThreadingHTTPServer(('127.0.0.1',PORT),h);threading.Thread(target=srv.serve_forever,daemon=True).start()
TL=json.load(open('timeline.json')); fps=30; n=int(TL['total']*fps)
ff=subprocess.Popen([FF,'-y','-loglevel','error','-f','image2pipe','-framerate',str(fps),'-i','-','-i','vo/full.wav',
 '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','out.mp4'],stdin=subprocess.PIPE)
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium'); pg=b.new_page(viewport={'width':1080,'height':1920})
  pg.goto(f'http://127.0.0.1:{PORT}/anim.html'); pg.evaluate('window.ready')
  for f in range(n):
    d=pg.evaluate(f'frame({f/fps})'); ff.stdin.write(base64.b64decode(d.split(',')[1]))
ff.stdin.close(); ff.wait(); print('frames',n)
