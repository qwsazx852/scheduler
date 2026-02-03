import os
import uuid
import asyncio
import subprocess
from flask import Flask, request, jsonify, send_from_directory, url_for
import edge_tts

app = Flask(__name__)

# 設定儲存音檔的資料夾 (使用絕對路徑，確保 n8n 找得到)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# 支援的聲音列表 (建議換成曉雨，聲音比較年輕甜美，符合 Sherry 形象)
DEFAULT_VOICE = "zh-TW-HsiaoYuNeural"

def get_audio_duration_ms(file_path):
    """
    使用 ffprobe (或是 ffmpeg) 取得音檔長度 (毫秒)
    LINE Message 需要毫秒整數
    """
    try:
        # 使用 ffprobe 取得 duration
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        duration_sec = float(result.stdout)
        return int(duration_sec * 1000)
    except Exception as e:
        print(f"Error getting duration: {e}")
        return 1000 # Default to 1 sec if failed

async def generate_audio_file(text, voice, output_path):
    # 先產生 mp3
    temp_mp3 = output_path.replace(".m4a", ".mp3")
    communicate = edge_tts.Communicate(text, voice)

    
    await communicate.save(temp_mp3)
    
    # 轉檔為 m4a (LINE 相容性較佳)
    try:
        from pydub import AudioSegment
        sound = AudioSegment.from_mp3(temp_mp3)
        sound.export(output_path, format="m4a")
        # 移除暫存 mp3
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)
    except Exception as e:
        print(f"Conversion failed: {e}. Keeping MP3.")
        # 如果轉檔失敗，就直接改名用 mp3 (雖然 LINE 支援度較差)
        os.rename(temp_mp3, output_path)

@app.route('/generate', methods=['POST'])
def generate_audio():
    data = request.json
    text = data.get('text')
    voice = data.get('voice', DEFAULT_VOICE)
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # 產生唯一的檔名 (強制使用 .m4a)
    filename = f"{uuid.uuid4()}.m4a"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    # 執行轉語音
    try:
        asyncio.run(generate_audio_file(text, voice, filepath))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 取得公開網址 (需要 ngrok 若是在本地測試)
    # 這裡我們先回傳相對路徑，使用者需自行組合 base URL
    # 或者我們嘗試從 request.host_url 組合
    # 注意：如果過 ngrok，request.host_url 可能是 http://localhost:5000/，需要手動替換成 ngrok url
    # 在 n8n 中，我們建議直接回傳完整的相對路徑，由 n8n 負責組合 Base URL (ngrok url)
    
    file_url_path = f"/static/audio/{filename}"
    
    # 計算長度
    duration = get_audio_duration_ms(filepath)
    
    return jsonify({
        "success": True,
        "filename": filename,
        "path": file_url_path,
        "duration": duration,
        "message": "Audio generated successfully"
    })

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

@app.route('/', methods=['GET'])
def index():
    return "TTS Server is running. Use POST /generate to create audio."

if __name__ == '__main__':
    print("Starting TTS Server on port 5002...")
    print("Make sure you have ffmpeg installed for duration calculation.")
    print("Usage: python3 tts_server.py")
    app.run(host='0.0.0.0', port=5002)
