import subprocess
import os
import threading
import requests
import zipfile
import io
from flask import Flask, render_template_string

app = Flask(__name__)

# --- Minecraftサーバーの設定 ---
SERVER_EXECUTABLE = "./bedrock_server"
# Linux版 Bedrock Dedicated ServerのダウンロードURL
SERVER_URL = "https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.21.102.1.zip"

server_process = None
process_lock = threading.Lock()

# HTMLテンプレート (変更なし)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Minecraft サーバー管理</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; }
        .status { font-size: 24px; font-weight: bold; }
        .controls { margin-top: 20px; }
        button { padding: 10px 20px; font-size: 16px; margin: 5px; cursor: pointer; }
        button:disabled { background-color: #ccc; cursor: not-allowed; }
    </style>
</head>
<body>
    <h1>Minecraft サーバー管理パネル</h1>
    <p>サーバーの状態: <span class="status">{{ status }}</span></p>
    <div class="controls">
        <form action="/start" method="post" style="display:inline;">
            <button type="submit" {% if status == '起動中' %}disabled{% endif %}>サーバーを起動</button>
        </form>
        <form action="/stop" method="post" style="display:inline;">
            <button type="submit" {% if status == '停止中' %}disabled{% endif %}>サーバーを停止</button>
        </form>
    </div>
</body>
</html>
"""

def download_and_extract_server():
    """Minecraftサーバーをダウンロード・展開する関数"""
    print("Minecraftサーバーのファイルが見つかりません。ダウンロードを開始します...")
    try:
        r = requests.get(SERVER_URL, stream=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(".") # カレントディレクトリに展開
        print("ダウンロードと展開が完了しました。")
        # 実行権限を付与
        os.chmod(SERVER_EXECUTABLE, 0o755)
    except Exception as e:
        print(f"ダウンロードまたは展開中にエラーが発生しました: {e}")

@app.route("/")
def index():
    with process_lock:
        status = "起動中" if server_process and server_process.poll() is None else "停止中"
    return render_template_string(HTML_TEMPLATE, status=status)

@app.route("/start", methods=["POST"])
def start_server():
    global server_process
    with process_lock:
        if server_process is None or server_process.poll() is not None:
            # サーバー実行ファイルが存在するかチェック
            if not os.path.exists(SERVER_EXECUTABLE):
                download_and_extract_server()
                
            server_process = subprocess.Popen([SERVER_EXECUTABLE], preexec_fn=os.setsid)
    return index()

@app.route("/stop", methods=["POST"])
def stop_server():
    global server_process
    with process_lock:
        if server_process and server_process.poll() is None:
            os.killpg(os.getpgid(server_process.pid), 9)
            server_process.wait()
            server_process = None
    return index()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
