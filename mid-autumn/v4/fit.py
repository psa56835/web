# 構圖控制：把角色縮到安全區內（置中偏上），周圍用 SDXL 外擴補畫
# python3 fit.py jobs_fit.json   jobs=[[src, out, prompt, 角色最大高度(畫面px), seed], ...]
import sys, os, json, time, numpy as np, cv2, torch
from PIL import Image, ImageFilter
from rembg import remove, new_session
from diffusers import StableDiffusionXLInpaintPipeline, StableDiffusionXLImg2ImgPipeline, DPMSolverMultistepScheduler
torch.set_num_threads(4)

CW, CH = 832, 1472                     # 補畫畫布（之後放大成 1210x2150 = 畫面 1.12 倍）
K = CH / (1920 * 1.12)                 # 畫面 px → 畫布 px
TARGET_CY = (820 + 1920 * .06) * K     # 角色中心放在畫面 y≈820（安全區置中偏上）
STYLE = "soft 3d cartoon render, pixar style, warm cinematic light, highly detailed"
NEG = "text, watermark, deformed, extra head, extra limbs, frame, border, seam"
seg = new_session('birefnet-general-lite')
pipe = None


def get_pipe():
    global pipe
    if pipe is None:
        pipe = StableDiffusionXLInpaintPipeline.from_pretrained('Lykon/dreamshaper-xl-lightning', variant='fp16', torch_dtype=torch.bfloat16)
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, algorithm_type='sde-dpmsolver++', use_karras_sigmas=True)
        pipe.set_progress_bar_config(disable=True)
    return pipe


for src, out, prompt, max_h, seed in json.load(open(sys.argv[1])):
    if os.path.exists(out):
        continue
    t0 = time.time()
    im = Image.open(src).convert('RGB')
    a = np.array(remove(im, session=seg).getchannel('A')) > 60
    ys, xs = np.where(a)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    # 縮放：角色高度不超過 max_h（畫面 px），且整張圖至少蓋滿畫布寬
    s = min(max_h * K / (by1 - by0), 1.25 * CW / im.width)
    s = max(s, 0.4 * CW / im.width)
    sw, sh = round(im.width * s), round(im.height * s)
    small = im.resize((sw, sh), Image.LANCZOS)
    cx, cy = (bx0 + bx1) / 2 * s, (by0 + by1) / 2 * s
    ox, oy = round(CW / 2 - 45 * K - cx), round(TARGET_CY - cy)   # 安全區中心 x≈495
    if sw >= CW:
        ox = min(max(ox, CW - sw), 0)                               # 夠寬就不留左右空白
    canvas = np.zeros((CH, CW, 3), np.uint8); known = np.zeros((CH, CW), np.uint8)
    x0, y0 = max(ox, 0), max(oy, 0); x1, y1 = min(ox + sw, CW), min(oy + sh, CH)
    canvas[y0:y1, x0:x1] = np.array(small)[y0 - oy:y1 - oy, x0 - ox:x1 - ox]; known[y0:y1, x0:x1] = 255
    inner = cv2.erode(known, np.ones((25, 25), np.uint8))           # 邊界往內 12px 也重畫，接縫才自然
    mask = Image.fromarray(255 - inner).filter(ImageFilter.GaussianBlur(8))
    init = Image.fromarray(cv2.inpaint(canvas, 255 - known, 15, cv2.INPAINT_TELEA))
    res = get_pipe()(prompt=prompt + ', ' + STYLE, negative_prompt=NEG, image=init, mask_image=mask, width=CW, height=CH,
                     strength=0.99, num_inference_steps=8, guidance_scale=2.0, generator=torch.Generator().manual_seed(seed)).images[0]
    # 原圖區域貼回（保留角色原始細節），邊緣柔和過渡
    m = np.array(mask, np.float32)[..., None] / 255
    fin = (np.array(res, np.float32) * m + np.array(init, np.float32) * (1 - m)).astype(np.uint8)
    Image.fromarray(fin).resize((round(1080 * 1.12), round(1920 * 1.12)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 60, 2)).save(out)
    print(out, f'{time.time() - t0:.0f}s scale={s * im.width / CW:.2f}', flush=True)
