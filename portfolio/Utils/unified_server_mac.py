import os
import uuid
import subprocess
import requests
from flask import Flask, request, jsonify, send_from_directory, Response

app = Flask(__name__)

# Configuration
N8N_URL = "http://localhost:5678"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")
DEFAULT_VOICE = "zh-TW-HsiaoYuNeural"
VOICE_MODE = True 

# Mac Native Voice Fallback
MAC_VOICE_NAME = "Meijia" 

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

def generate_audio_file_mac(text, voice, output_path):
    """
    Use macOS 'say' command for robust offline TTS
    """
    cmd = ["say", "-v", MAC_VOICE_NAME, "-o", output_path, text]
    print(f"[Mac TTS] Executing: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Mac 'say' command failed: {result.stderr}")

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
    # Check Voice Mode 
    # if not VOICE_MODE: ...

    data = request.json
    text = data.get('text')
    
    # Ignore specific Edge voice config, use Mac Native
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    filename = f"{uuid.uuid4()}.m4a"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    try:
        # Use Mac Native Generator
        generate_audio_file_mac(text, MAC_VOICE_NAME, filepath)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    file_url_path = f"/static/audio/{filename}" 
    duration = get_audio_duration_ms(filepath)
    
    return jsonify({
        "success": True,
        "filename": filename,
        "path": file_url_path,
        "duration": duration,
        "provider": f"Mac Native ({MAC_VOICE_NAME})"
    })

# 2. File Serving 
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
    url = f"{N8N_URL}/{path}"
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
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return jsonify({"error": f"Failed to connect to n8n: {str(e)}"}), 502

if __name__ == '__main__':
    print(f"Starting Unified Server (Mac Native) on port {PORT}...")
    print("This server handles TTS (via 'say' command) and proxies to n8n.")
    app.run(host='0.0.0.0', port=PORT)
