# 補鏡頭：天空底圖、國王生氣（以戴皇冠那張為底 img2img，保持同一張臉）
import torch, time
from PIL import Image, ImageFilter
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline, DPMSolverMultistepScheduler
torch.set_num_threads(4)
STYLE = "soft 3d cartoon render, pixar style, warm cinematic light, highly detailed"
base = StableDiffusionXLPipeline.from_pretrained('Lykon/dreamshaper-xl-lightning', variant='fp16', torch_dtype=torch.bfloat16)
base.scheduler = DPMSolverMultistepScheduler.from_config(base.scheduler.config, algorithm_type='sde-dpmsolver++', use_karras_sigmas=True)
base.set_progress_bar_config(disable=True)
big = lambda im: im.resize((1210, 2150), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 60, 2))
t = time.time()
sky = base(prompt="vast bright hot hazy golden sky filling the frame, soft clouds, tiny desert village rooftops at the very bottom, " + STYLE,
           negative_prompt="sun, people, text, watermark", width=832, height=1472, num_inference_steps=6, guidance_scale=2.0,
           generator=torch.Generator().manual_seed(801)).images[0]
big(sky).save('plates/s2s.png'); print('sky', time.time() - t, flush=True)
i2i = StableDiffusionXLImg2ImgPipeline(**base.components)
src = Image.open('plates/s4c.png').convert('RGB').resize((832, 1472), Image.LANCZOS)
for seed in (811, 812):
    t = time.time()
    im = i2i(prompt="cute chibi boy king with an angry frowning face, furrowed eyebrows, pouting, grumpy, red royal robe, golden crown, dim red palace, " + STYLE,
             negative_prompt="smile, happy, deformed, extra head, text", image=src, strength=0.45, num_inference_steps=12, guidance_scale=2.0,
             generator=torch.Generator().manual_seed(seed)).images[0]
    big(im).save(f'raw/s4b_i2i_{seed}.png'); print('angry', seed, time.time() - t, flush=True)
