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

# --- Mock ERP (Digital Twin) ---
@app.route('/mock_erp')
def mock_erp_ui():
    html = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <title>T100 ERP - Sales Order Entry (Simulation)</title>
        <style>
            body { font-family: 'Arial', sans-serif; background-color: #f0f0f0; padding: 20px; }
            .container { background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; border-top: 5px solid #007bff; }
            h2 { color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
            input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            .btn-group { margin-top: 20px; text-align: right; }
            button { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
            .btn-save { background-color: #28a745; color: white; }
            .btn-cancel { background-color: #dc3545; color: white; margin-left: 10px; }
            #status { margin-top: 20px; padding: 10px; display: none; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>T100 銷售訂單維護作業 (axmt500)</h2>
            <div class="form-group">
                <label>客戶編號 (Customer ID)</label>
                <input type="text" value="CUST_001">
            </div>
            <div class="form-group">
                <label>訂單單號 (Order No)</label>
                <input type="text" value="AUTO_GEN_20260207" readonly style="background: #eee;">
            </div>
            <div class="form-group">
                <label>產品料號 (Part No)</label>
                <input type="text" id="partNo" placeholder="請輸入料號...">
            </div>
            <div class="form-group">
                <label>訂購數量 (Quantity)</label>
                <input type="number" id="qty" placeholder="請輸入數量...">
            </div>
            
            <div class="btn-group">
                <button class="btn-save" onclick="saveOrder()">存檔 (Save)</button>
                <button class="btn-cancel">離開 (Exit)</button>
            </div>
            <div id="status"></div>
        </div>

        <script>
            function saveOrder() {
                const partNo = document.getElementById('partNo').value;
                const qty = document.getElementById('qty').value;
                const statusDiv = document.getElementById('status');
                
                if(!partNo || !qty) {
                    alert("請輸入料號與數量！");
                    return;
                }

                statusDiv.style.display = 'block';
                statusDiv.style.backgroundColor = '#e2e6ea';
                statusDiv.innerHTML = "Processing...";

                // Simulate API Call
                fetch('/mock_api/order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ part_no: partNo, quantity: qty })
                })
                .then(response => response.json())
                .then(data => {
                    statusDiv.style.backgroundColor = '#d4edda';
                    statusDiv.style.color = '#155724';
                    statusDiv.innerHTML = `訂單建立成功 (Success)! <br> ERP 單號: ${data.erp_id}`;
                })
                .catch(error => {
                    statusDiv.style.backgroundColor = '#f8d7da';
                    statusDiv.style.color = '#721c24';
                    statusDiv.innerHTML = "連線失敗 (Connection Error)";
                });
            }
        </script>
    </body>
    </html>
    """
    return Response(html, mimetype='text/html; charset=utf-8')

@app.route('/mock_api/order', methods=['POST'])
def mock_create_order():
    data = request.json
    return jsonify({
        "status": "success",
        "message": "Order created in T100",
        "erp_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
        "details": data
    })

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
