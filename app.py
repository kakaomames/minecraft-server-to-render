import subprocess
import os
import threading
import requests
import zipfile
import io
import configparser
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# --- Minecraftサーバーの設定 ---
SERVER_EXECUTABLE = "./bedrock_server"
SERVER_URL = "https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.21.102.1.zip"
PROPERTIES_FILE = "./server.properties"

server_process = None
process_lock = threading.Lock()

# HTMLテンプレートを更新
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Minecraft サーバー管理</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; }
        .status { font-size: 24px; font-weight: bold; }
        .controls, .settings { margin-top: 20px; }
        button { padding: 10px 20px; font-size: 16px; margin: 5px; cursor: pointer; }
        button:disabled { background-color: #ccc; cursor: not-allowed; }
        .settings-form { max-width: 600px; margin: 20px auto; text-align: left; border: 1px solid #ccc; padding: 20px; border-radius: 8px; }
        .settings-form label { display: block; margin: 10px 0 5px; font-weight: bold; }
        .settings-form input[type="text"] { width: 95%; padding: 8px; }
        .settings-form input[type="submit"] { background-color: #4CAF50; color: white; border: none; padding: 10px 20px; cursor: pointer; margin-top: 20px; }
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

    <hr>
    
    <h2>サーバー設定</h2>
    <div class="settings">
        <form action="/save_settings" method="post" class="settings-form">
            {% for key, value in settings.items() %}
                <label for="{{ key }}">{{ key }}</label>
                <input type="text" id="{{ key }}" name="{{ key }}" value="{{ value }}">
            {% endfor %}
            <input type="submit" value="設定を保存">
        </form>
    </div>
</body>
</html>
"""

def download_and_extract_server():
    print("Minecraftサーバーのファイルが見つかりません。ダウンロードを開始します...")
    try:
        r = requests.get(SERVER_URL, stream=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(".")
        print("ダウンロードと展開が完了しました。")
        os.chmod(SERVER_EXECUTABLE, 0o755)
    except Exception as e:
        print(f"ダウンロードまたは展開中にエラーが発生しました: {e}")

def read_server_properties():
    """server.propertiesファイルを読み込み、辞書として返す"""
    config = configparser.ConfigParser()
    config.optionxform = str  # キー名を小文字に変換しないようにする
    config.read_string("[server_settings]\n" + open(PROPERTIES_FILE, 'r').read())
    return dict(config['server_settings'])

def write_server_properties(settings):
    """辞書の内容をserver.propertiesファイルに書き込む"""
    with open(PROPERTIES_FILE, 'w') as f:
        for key, value in settings.items():
            f.write(f"{key}={value}\n")

@app.route("/")
def index():
    with process_lock:
        status = "起動中" if server_process and server_process.poll() is None else "停止中"

    settings = {}
    if os.path.exists(PROPERTIES_FILE):
        settings = read_server_properties()
    
    return render_template_string(HTML_TEMPLATE, status=status, settings=settings)

@app.route("/save_settings", methods=["POST"])
def save_settings():
    # POSTされたフォームデータを取得し、設定ファイルに書き込む
    settings = request.form
    if settings:
        write_server_properties(settings)
    return redirect(url_for('index'))

@app.route("/start", methods=["POST"])
def start_server():
    global server_process
    with process_lock:
        if server_process is None or server_process.poll() is not None:
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
