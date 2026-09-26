# 逐子句合成 + whisper 驗字，不合格重生，最後依標點補停頓串接
import sys, re, json, difflib, numpy as np, torch; sys.argv=['x']
import shim, runpy, soundfile as sf, whisper, opencc
g = runpy.run_path('single_inference.py', run_name='lib')
from g2pw import G2PWConverter
cv = g['CustomCosyVoice']('MediaTek-Research/BreezyVoice-300M'); bc = G2PWConverter()
asr = whisper.load_model('small'); s2t = opencc.OpenCC('s2twp')
P = "在密碼學中，加密是將明文資訊改變為難以讀取的密文內容，使之不可讀的方法。"
pr16 = g['load_wav']('data/prompt9.wav', 16000)
pt = g['get_bopomofo_rare'](cv.frontend.text_normalize_new(P, split=False), bc)
L = json.load(open('lines.json'))
han = lambda s: re.sub(r'[^一-鿿]', '', s)
def synth(t, seed):
    torch.manual_seed(seed)
    tb = g['get_bopomofo_rare'](cv.frontend.text_normalize_new(t, split=False), bc)
    mi = cv.frontend.frontend_zero_shot(tb, pt, pr16)
    return cv.model.inference(**mi)['tts_speech'][0].numpy()
def trim(y, sr=22050):
    i = np.where(np.abs(y) > 0.01)[0]
    return y[max(0, i[0]-400): i[-1]+1500] if len(i) else y
for li, line in L.items():
    parts = [p for p in re.findall(r'[^，、。！？]+[，、。！？]?', line)]
    out = []
    for p in parts:
        best = None
        for att in range(3):
            y = trim(synth(p.rstrip('，、。！？'), 1000*att + len(p)))
            sf.write('tmp.wav', y, 22050)
            txt = s2t.convert(asr.transcribe('tmp.wav', language='zh', initial_prompt='以下是繁體中文的句子。')['text'])
            sc = difflib.SequenceMatcher(None, han(p), han(txt)).ratio()
            cps = len(han(p)) / (len(y)/22050)
            if 2.2 < cps < 6.5: sc += 0.001
            else: sc -= 0.3
            print(li, repr(p), att, round(sc,2), round(cps,1), txt, flush=True)
            if best is None or sc > best[0]: best = (sc, y)
            if sc >= 0.85: break
        out.append(best[1])
        gap = {'，':.16,'、':.12,'。':.4,'！':.4,'？':.4}.get(p[-1], .1)
        out.append(np.zeros(int(22050*gap)))
    sf.write(f'vo/l{li}.wav', np.concatenate(out[:-1]), 22050)
    print('LINE', li, 'saved', flush=True)
print('ALLDONE')
