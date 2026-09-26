# 中秋動畫 v2 交接

## 需求（使用者確認）
- 9:16（1080x1920），總長 60 秒內
- 有語音、無字幕、無配樂
- 語音全部台灣口音，用開源模型：BreezyVoice（MediaTek-Research/BreezyVoice）
- 第一段：媽媽在床上擁抱熊寶（角色依 `src/cut/` 與原設定圖），媽媽說：
  「今天中秋節～ 媽媽說個中秋節故事給你聽～」
- 之後的故事只出現故事角色（后羿、嫦娥、百姓），不再出現媽媽和熊寶
- 場景之間硬切，畫風可愛童趣，色系沿用設定圖色票：
  #FFF6EE #E7D6C1 #D9A8B1 #CDB7E9 #8C6B57 #B9CDE6 #C9D6EA
- 方案 A：全部在雲端容器內完成（無 GPU，4 核 CPU，15GB RAM）
  - 故事插畫：SD-Turbo / SDXL-Turbo（CPU）產Q版繪本風插畫
  - 動畫：去背拆層 + 2D 動態（推移、飄浮、射箭軌跡、粒子），逐格輸出
  - 第一段擁抱畫面：試 (1) 設定圖全身去背拼擁抱姿勢再 img2img 修接縫 (2) 直接生成挑最像的，不夠像要跟使用者說

## 旁白（台灣口語，約 55 秒）
1. 今天中秋節～ 媽媽說個中秋節故事給你聽～
2. 很久很久以前，天上有十個太陽，熱到土地都裂開了，大家都好辛苦喔。
3. 有個叫后羿的大哥哥，爬到高高的山上，咻、咻、咻，射下九個太陽，只留一個，每天準時上班下班。
4. 大家請他當國王，可是他變得好兇，還拿到吃了會長生不老的仙丹。
5. 他的太太嫦娥好擔心，偷偷把仙丹吃掉，結果身體輕飄飄的，一路飛到月亮上。
6. 後來每年八月十五，大家就一起賞月、吃月餅，謝謝善良的嫦娥。這就是中秋節喔！

## 既有素材
- `src/cut/m0-m3.png`：媽媽四個表情去背（自信、擔心、開心、思考）
- `src/cut/k0-k3.png`：熊寶四個表情去背（乖巧、委屈、開心、好奇）
- 原設定圖需使用者重新上傳（全身正面去背要重做）
- v1 成品 `mid-autumn-story.mp4` 使用者評為品質不行，v2 全部重做

## v2 進度（方案 A 已完成初版）
- 成品：`mid-autumn-story-v2.mp4`（1080x1920、56.3 秒、只有語音）
- 語音：BreezyVoice-300M（CPU），參考聲音用官方 `data/example.wav` 的前 9 秒，逐子句合成再用 whisper 驗字（`v2/tts/tts2.py`、`v2/tts/shim.py`，torchaudio 新版要用 shim 墊 soundfile）
  - 要先 clone mtkresearch/BreezyVoice，把 processor.py 的 `set_audio_backend` 註解掉，並裝 `ruamel.yaml<0.18`
  - 第 1 句用的是完整 17 秒參考音，其餘用 9 秒版，音色可能有一點差異
  - 待確認：第 3 句「射下」whisper 一直聽成「受下」
- 插畫：SDXL-Turbo bf16 CPU（`v2/gen.py`，jobs.json / jobs2.json 是 prompt），`v2/prep.py` 負責去背（isnet-anime，太陽和月餅改用 birefnet）和調色
- 動畫：`v2/engine.py` 合成引擎、`v2/s1.py` 開場床戲（被子前景遮罩）、`v2/scenes.py` 第 2～6 段，`python3 render.py out.mp4 vo` 輸出
- 注意：SDXL 和 TTS 同時跑會 OOM（15GB），要排隊跑

## v3（使用者否決 v2 去背拼貼，改程式繪製動畫）
- 需求以 `PROMPT-v3.md` 為準
- Voai ConnectAPI（https://connect.voai.ai/docs）需要 x-api-key，沒帶 key 回 401
  若無 key：使用者從 app.voai.ai 網頁版生成 6 句音檔上傳，我再對時間軸
