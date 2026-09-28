# SDXL-Turbo CPU 生圖：python3 gen.py out.png "prompt" [W H seed steps]
import sys, torch, time
from diffusers import AutoPipelineForText2Image
torch.set_num_threads(int(__import__('os').environ.get('NT', '4')))
STYLE = "high quality, adorable"
NEG = "ugly, scary, realistic photo, text, watermark, deformed, extra limbs, dark, horror"
_pipe = None
def pipe():
    global _pipe
    if _pipe is None:
        _pipe = AutoPipelineForText2Image.from_pretrained('stabilityai/sdxl-turbo', variant='fp16', torch_dtype=getattr(torch, __import__('os').environ.get('DT','float32')))
        _pipe.set_progress_bar_config(disable=True)
    return _pipe
def gen(out, prompt, W=576, H=1024, seed=0, steps=2):
    t = time.time()
    img = pipe()(prompt=prompt + ', ' + STYLE, width=W, height=H, num_inference_steps=steps, guidance_scale=0.0,
                 generator=torch.Generator().manual_seed(seed)).images[0]
    img.save(out); print(out, f'{time.time()-t:.1f}s', flush=True)
if __name__ == '__main__':
    import json
    for j in json.load(open(sys.argv[1])):  # [[out, prompt, W, H, seed, steps], ...]
        if not __import__('os').path.exists(j[0]):
            gen(*j)
