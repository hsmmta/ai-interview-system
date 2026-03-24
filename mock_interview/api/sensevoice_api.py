from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from funasr import AutoModel
import librosa
import re
import os
import shutil

app = FastAPI()

# 允许跨域请求（极其重要，否则你的 JSP 网页调不通这个接口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("⏳ 正在全局加载 SenseVoice 模型...")
model = AutoModel(model="iic/SenseVoiceSmall", trust_remote_code=True, remote_code="./model.py", device="cuda:0")

@app.post("/api/analyze-interview")
async def analyze_audio_api(audio_file: UploadFile = File(...)):
    # 1. 接收前端发来的音频，存为临时文件
    temp_path = f"temp_{audio_file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    try:
        # 2. 使用咱们刚才写的硬核 Librosa 逻辑解析音频
        audio_array, _ = librosa.load(temp_path, sr=16000)
        res = model.generate(input=audio_array, cache={}, language="zh", use_itn=True, batch_size_s=60)

        raw_text = res[0]['text']

        # 3. 清洗数据
        emotions = re.findall(r'<\|(HAPPY|SAD|ANGRY|NEUTRAL)\|>', raw_text)
        emotion = emotions[0] if emotions else "NEUTRAL"
        events = list(set(re.findall(r'<\|(Laughter|Sigh|Cough|Speech|BGM)\|>', raw_text)))
        clean_text = re.sub(r'<\|.*?\|>', '', raw_text).strip()

        # 4. 删掉临时文件
        os.remove(temp_path)

        # 5. 返回完美的 JSON 给你的 JSP 网站
        return {
            "code": 200,
            "data": {
                "candidate_text": clean_text,
                "emotion": emotion,
                "events": events
            }
        }
    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return {"code": 500, "msg": str(e)}

if __name__ == "__main__":
    import uvicorn
    # 启动服务，运行在本地的 8020 端口
    uvicorn.run(app, host="0.0.0.0", port=8020)