# 由語音停頓算出每個子句的開始時間，產生動畫對時 cues.json
# python3 cues.py ../v2/vo   （時間 = 段內秒數，已含 PRE 留白）
import sys, re, json, numpy as np, soundfile as sf

PRE = 0.35
LINES = {
    1: "今天中秋節！媽媽說個中秋節故事給你聽！",
    2: "很久很久以前，天上有十個太陽，熱到土地都裂開了，大家都好辛苦喔。",
    3: "有個叫后羿的大哥哥，爬到高高的山上，咻！咻！咻！射下九個太陽，只留一個，每天準時上班下班。",
    4: "大家請他當國王，可是他變得好兇，還拿到吃了會長生不老的仙丹。",
    5: "他的太太嫦娥好擔心，偷偷把仙丹吃掉，結果身體輕飄飄的，一路飛到月亮上。",
    6: "後來每年八月十五，大家就一起賞月、吃月餅，謝謝善良的嫦娥。這就是中秋節喔！",
}


def phrase_starts(path, n):
    y, sr = sf.read(path)
    y = y if y.ndim == 1 else y.mean(1)
    fr = int(sr * 0.01)
    e = np.array([np.abs(y[i:i + fr]).max() for i in range(0, len(y) - fr, fr)]) > 0.015
    gaps, i = [], 0  # (長度, 結束點) 的靜音段
    while i < len(e):
        if not e[i]:
            j = i
            while j < len(e) and not e[j]:
                j += 1
            if i > 0 and j < len(e):
                gaps.append((j - i, j))
            i = j
        else:
            i += 1
    cut = sorted(g[1] for g in sorted(gaps, reverse=True)[:n - 1])
    first = int(np.argmax(e))
    return [round(PRE + k * 0.01, 2) for k in [first] + cut]


vo = sys.argv[1]
P = {i: phrase_starts(f'{vo}/l{i}.wav', len(re.findall(r'[^，、。！？]+[，、。！？]', t))) for i, t in LINES.items()}
for i, p in P.items():
    print(i, p)
p2, p3, p4, p5, p6 = P[2], P[3], P[4], P[5], P[6]
cues = {
    '2': {'suns': p2[1], 'crack': p2[2], 'hard': p2[3]},
    '3': {'climbStart': p3[1], 'climb': p3[2] - 0.2, 'shots': [p3[2], p3[3], p3[4]], 'work': p3[7]},
    '4': {'crown': p4[0] + 0.4, 'angry': p4[1], 'pill': p4[2] + 0.3},
    '5': {'eat': p5[1] + 0.9, 'fly': p5[2]},
    '6': {'thank': p6[3]},
}
json.dump(cues, open('cues.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(cues, ensure_ascii=False))
