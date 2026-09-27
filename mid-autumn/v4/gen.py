# DreamShaper XL Lightning（CPU bf16）生成分鏡圖風格場景
# python3 gen.py jobs.json   jobs=[[out, prompt, W, H, seed], ...]
import sys, os, json, time, torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
torch.set_num_threads(4)
STYLE = ("soft 3d cartoon render, pixar style, chibi, glossy big eyes, warm cinematic light, highly detailed")
NEG = "2d, flat, anime, sketch, lowres, deformed, extra head, extra limbs, bad hands, text, watermark, scary, realistic photo"
pipe = StableDiffusionXLPipeline.from_pretrained('Lykon/dreamshaper-xl-lightning', variant='fp16', torch_dtype=torch.bfloat16)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, algorithm_type='sde-dpmsolver++', use_karras_sigmas=True)
pipe.set_progress_bar_config(disable=True)
for out, prompt, w, h, seed in json.load(open(sys.argv[1])):
    if os.path.exists(out):
        continue
    t = time.time()
    img = pipe(prompt=prompt + ', ' + STYLE, negative_prompt=NEG, width=w, height=h, num_inference_steps=6, guidance_scale=2.0,
               generator=torch.Generator().manual_seed(seed)).images[0]
    img.save(out); print(out, f'{time.time() - t:.0f}s', flush=True)
