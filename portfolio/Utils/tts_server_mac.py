import os
import uuid
import subprocess
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Mac Native Voice
DEFAULT_VOICE = "Meijia"

def get_audio_duration_ms(file_path):
    """
    Get duration using ffprobe
    """
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

def generate_audio_file(text, voice, output_path):
    """
    Use macOS 'say' command
    """
    # Mac 'say' determines format by extension. .m4a works natively.
    cmd = ["say", "-v", voice, "-o", output_path, text]
    print(f"Executing: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Mac 'say' command failed: {result.stderr}")

@app.route('/generate', methods=['POST'])
def generate_audio():
    data = request.json
    text = data.get('text')
    
    # Map Edge-TTS voice names to Mac Voice if passed, or use Default
    requested_voice = data.get('voice', DEFAULT_VOICE)
    if "Hsiao" in requested_voice or "YunJhe" in requested_voice:
        # Fallback to Meijia if client sends Edge voice names
        voice = "Meijia"
    else:
        voice = requested_voice

    if not text:
        return jsonify({"error": "No text provided"}), 400

    filename = f"{uuid.uuid4()}.m4a"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    try:
        generate_audio_file(text, voice, filepath)
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
        "message": "Audio generated successfully (Mac Native)"
    })

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

@app.route('/', methods=['GET'])
def index():
    return "TTS Server (Mac Native) is running."

if __name__ == '__main__':
    print("Starting Mac Native TTS Server on port 5002...")
    app.run(host='0.0.0.0', port=5002)
