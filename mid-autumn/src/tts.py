import sherpa_onnx, soundfile as sf, sys, numpy as np
D='kokoro-multi-lang-v1_1/'
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
 model=D+'model.onnx',voices=D+'voices.bin',tokens=D+'tokens.txt',data_dir=D+'espeak-ng-data',dict_dir=D+'dict',
 lexicon=D+'lexicon-us-en.txt,'+D+'lexicon-zh.txt'),num_threads=4),
 rule_fsts=D+'date-zh.fst,'+D+'phone-zh.fst,'+D+'number-zh.fst')
tts=sherpa_onnx.OfflineTts(cfg)
def gen(text,sid,speed,out):
  a=tts.generate(text,sid=sid,speed=speed); s=np.array(a.samples); sf.write(out,s,a.sample_rate); return len(s)/a.sample_rate
if __name__=='__main__':
  for sid in [3,4,5,6,7,8,10,13,20,30]:
    print(sid, gen('来，熊宝，妈妈讲中秋节的故事给你听，听完就要睡觉啰！',sid,0.95,f'v{sid}.wav'))
