import os
import uuid
import asyncio
import subprocess
import requests
from flask import Flask, request, jsonify, send_from_directory, Response
import edge_tts

app = Flask(__name__)

# Configuration
N8N_URL = "http://localhost:5678"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")
DEFAULT_VOICE = "zh-TW-HsiaoYuNeural"
VOICE_MODE = True # Default to ON (Reverted)

# --- 聲音設定區 (Voice Configuration) ---
# 您可以在這裡切換不同的聲音設定，只要把想要的設定解除註解 (拿掉 #) 即可

# 設定 1: 預設 Sherry (年輕甜美) - 目前使用
VOICE_CONFIG = {
    "voice": "zh-TW-HsiaoYuNeural",
    "rate": "+20%",   # 語速 (例如 +10% 會變快)
    "pitch": "+15Hz"  # 音調 (例如 +2Hz 會變高/更可愛)
}

# 設定 2: 蘿莉 Sherry (超可愛、講話快)
# VOICE_CONFIG = {
#     "voice": "zh-TW-HsiaoYuNeural",
#     "rate": "+15%",
#     "pitch": "+10Hz"
# }

# 設定 3: 成熟 Sherry (溫柔穩重)
# VOICE_CONFIG = {
#     "voice": "zh-TW-HsiaoChenNeural",
#     "rate": "-5%",
#     "pitch": "-2Hz"
# }

# 設定 4: 男聲助理 (清晰自然)
# VOICE_CONFIG = {
#     "voice": "zh-TW-YunJheNeural",
#     "rate": "+0%",
#     "pitch": "+0Hz"
# }

PORT = 5050

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# --- Helper Functions ---
def get_audio_duration_ms(file_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        duration_sec = float(result.stdout)
        return int(duration_sec * 1000)
    except Exception as e:
        print(f"Error getting duration: {e}")
        return 1000

async def generate_audio_file(text, voice, rate, pitch, output_path):
    temp_mp3 = output_path.replace(".m4a", ".mp3")
    # Apply rate and pitch
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(temp_mp3)
    try:
        from pydub import AudioSegment
        sound = AudioSegment.from_mp3(temp_mp3)
        # Force export as M4A with AAC codec and 44.1kHz (LINE standard)
        sound.export(
            output_path, 
            format="ipod", 
            codec="aac", 
            parameters=["-ac", "2", "-ar", "44100"]
        )
        if os.path.exists(temp_mp3): os.remove(temp_mp3)
    except Exception as e:
        print(f"Conversion failed: {e}. Keeping MP3.")
        os.rename(temp_mp3, output_path)

# --- Routes ---

# 0. Voice Control
@app.route('/voice/on', methods=['GET', 'POST'])
def voice_on():
    global VOICE_MODE
    VOICE_MODE = True
    return jsonify({"mode": True, "message": "Voice Mode ON"})

@app.route('/voice/off', methods=['GET', 'POST'])
def voice_off():
    global VOICE_MODE
    VOICE_MODE = False
    return jsonify({"mode": False, "message": "Voice Mode OFF"})

@app.route('/voice/status', methods=['GET'])
def voice_status():
    return jsonify({"mode": VOICE_MODE})

# 1. TTS Generation
@app.route('/generate', methods=['POST'])
def generate_audio():
    # Check Voice Mode (Disabled: Always generate)
    # if not VOICE_MODE:
    #     return jsonify({
    #         "success": False, 
    #         "skipped": True, 
    #         "message": "Voice Mode is OFF"
    #     })

    data = request.json
    text = data.get('text')
    
    # 使用 VOICE_CONFIG 的設定
    voice = VOICE_CONFIG.get("voice", DEFAULT_VOICE)
    rate = VOICE_CONFIG.get("rate", "+0%")
    pitch = VOICE_CONFIG.get("pitch", "+0Hz")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    filename = f"{uuid.uuid4()}.m4a"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    try:
        asyncio.run(generate_audio_file(text, voice, rate, pitch, filepath))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    file_url_path = f"/static/audio/{filename}" # Relative path
    duration = get_audio_duration_ms(filepath)
    
    return jsonify({
        "success": True,
        "filename": filename,
        "path": file_url_path,
        "duration": duration
    })

# 2. File Serving (Supports Range Requests natively by Flask)
@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    response = send_from_directory(AUDIO_DIR, filename)
    if filename.endswith(".m4a"):
        response.headers["Content-Type"] = "audio/mp4"
    return response

# 3. Reverse Proxy to n8n (Catch-All)
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    # If it hit the specific routes above, Flask handles it.
    # Otherwise, forward to n8n.
    
    # Construct n8n URL
    url = f"{N8N_URL}/{path}"
    
    # Forward request
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            params=request.args,
            allow_redirects=False,
            stream=True
        )
        
        # Filter headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
                   
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return jsonify({"error": f"Failed to connect to n8n: {str(e)}"}), 502

if __name__ == '__main__':
    print(f"Starting Unified Server on port {PORT}...")
    print("This server handles TTS, File Serving, and proxies everything else to n8n.")
    print("Please point your ngrok to port 5050.")
    app.run(host='0.0.0.0', port=PORT)
