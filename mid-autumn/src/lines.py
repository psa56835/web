from tts import gen
import soundfile as sf, numpy as np, json
L=[
"来，熊宝，妈妈讲中秋节的故事给你听，听完就要睡觉喔！",
"很久以前，天上有十个太阳，一直都是白天，土地都晒裂了，大家热得受不了。",
"有个年轻人叫后羿，爬上高山，咻！咻！射下了九个太阳，只留一个，每天准时升起、下山。",
"大家请后羿当国王，可是他越来越凶，还拿到长生不老药，想永远当国王。",
"他的太太嫦娥很担心，偷偷吃下仙药，身体变得轻飘飘，一路飞到了月亮上。",
"后来每年八月十五，大家就赏月、拜月亮，谢谢嫦娥，这就是中秋节喔！",
"好了，熊宝晚安，做个圆圆的好梦。",
]
out=[]
for i,t in enumerate(L):
  gen(t,6,1.03,f'vo/l{i}.wav')
  y,sr=sf.read(f'vo/l{i}.wav'); idx=np.where(np.abs(y)>0.01)[0]
  y=y[max(0,idx[0]-800):idx[-1]+2400]; sf.write(f'vo/l{i}.wav',y,sr); out.append(len(y)/sr)
print([round(d,2) for d in out], round(sum(out),2), sr)
json.dump(out,open('vo/dur.json','w'))
