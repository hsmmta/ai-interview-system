from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from funasr import AutoModel
import librosa
import re
import os
import shutil
import wave
import numpy as np

app = FastAPI()

# 允许跨域请求（极其重要，否则你的 JSP 网页调不通这个接口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print(" 正在全局加载 SenseVoice 模型...")
model = AutoModel(model="iic/SenseVoiceSmall", trust_remote_code=True, device="cuda:0")

def load_audio_fallback(path):
    """
    使用 Python 原生 wave 库加载音频，作为 soundfile/ffmpeg 的兜底方案。
    仅支持 WAV 格式。
    """
    try:
        with wave.open(path, 'rb') as wf:
            # 读取参数
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            rate = wf.getframerate()
            frames = wf.getnframes()

            # 读取数据
            buffer = wf.readframes(frames)

            # 根据位深转换
            if width == 2:
                data = np.frombuffer(buffer, dtype=np.int16)
                # 归一化到 -1 ~ 1
                data = data.astype(np.float32) / 32768.0
            elif width == 1: # 8-bit unsigned
                data = np.frombuffer(buffer, dtype=np.uint8)
                data = (data.astype(np.float32) - 128.0) / 128.0
            else:
                # 其他格式暂不处理，直接返回 None 尝试让 upstream 处理
                print(f" Unsupported bit width: {width}")
                return None, None

            # 如果是多声道，转单声道 (取平均)
            if channels > 1:
                data = data.reshape(-1, channels)
                data = data.mean(axis=1)

            return data, rate
    except Exception as e:
        print(f" Wave module load failed: {e}")
        return None, None

@app.post("/api/analyze-interview")
async def analyze_audio_api(audio_file: UploadFile = File(...)):
    # 1. 接收前端发来的音频，存为临时文件
    temp_path = f"temp_{audio_file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    try:
        # 2. 尝试加载音频
        audio_data, sample_rate = load_audio_fallback(temp_path)

        input_data = None
        if audio_data is not None:
            print(f" 使用 Wave 库加载成功, sr={sample_rate}, shape={audio_data.shape}")
            #  核心修复：如果采样率不是 16000，强制重采样！
            if sample_rate != 16000:
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
                print(" 已强制重采样至 16000 Hz")

            input_data = audio_data
        else:
            print(" Wave 加载失败，尝试传路径给模型...")
            input_data = temp_path

        # 3. 推理
        # cache={} is required for some versions of funasr to avoid errors
        res = model.generate(input=input_data, cache={}, language="zh", use_itn=True, batch_size_s=60)

        # 检查返回结果格式
        if not res or len(res) == 0:
            raise ValueError("模型识别结果为空")

        raw_text = res[0]['text']
        print(f" 识别成功: {raw_text}")

        # 3. 清洗数据
        emotions = re.findall(r'<\|(HAPPY|SAD|ANGRY|NEUTRAL)\|>', raw_text)
        emotion = emotions[0] if emotions else "NEUTRAL"
        events = list(set(re.findall(r'<\|(Laughter|Sigh|Cough|Speech|BGM)\|>', raw_text)))
        clean_text = re.sub(r'<\|.*?\|>', '', raw_text).strip()

        # 4. 删掉临时文件
        try:
            os.remove(temp_path)
        except:
            pass

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
        import traceback
        error_msg = f"{str(e)}"
        print(f" 识别出错: {error_msg}")
        traceback.print_exc() # 打印堆栈到控制台

        # 尝试清理
        if os.path.exists(temp_path):
            try: os.remove(temp_path)
            except: pass

        return {"code": 500, "msg": error_msg}

if __name__ == "__main__":
    import uvicorn
    # 启动服务，运行在本地的 8020 端口
    uvicorn.run(app, host="0.0.0.0", port=8020)