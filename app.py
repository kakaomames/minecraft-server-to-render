import subprocess
import os
import threading
from flask import Flask, render_template_string

# Flaskアプリケーションを初期化
app = Flask(__name__)

# --- Minecraftサーバーの設定 ---
# Minecraftサーバーの実行ファイルを指定
# Render上で動かすので、実行ファイルはプロジェクトのルートに配置します
# Linux環境なので、実行権限を付与しておきましょう
SERVER_EXECUTABLE = "./bedrock_server"

# サーバープロセスを管理するためのグローバル変数
# threading.Lockは、複数のリクエストが同時にサーバーの状態を変更するのを防ぐために使います
server_process = None
process_lock = threading.Lock()

# HTMLテンプレート
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

# ルートURL（/）にアクセスしたときに表示するページ
@app.route("/")
def index():
    with process_lock:
        status = "起動中" if server_process and server_process.poll() is None else "停止中"
    return render_template_string(HTML_TEMPLATE, status=status)

# サーバーを起動するエンドポイント
@app.route("/start", methods=["POST"])
def start_server():
    global server_process
    with process_lock:
        if server_process is None or server_process.poll() is not None:
            # サーバーの実行ファイルに実行権限を付与（Render環境向け）
            if not os.access(SERVER_EXECUTABLE, os.X_OK):
                os.chmod(SERVER_EXECUTABLE, 0o755)
            # `subprocess.Popen`を使って、サーバーを新しいプロセスとして起動
            # `preexec_fn=os.setsid` は、Webサービスが停止してもサーバープロセスが生き残るようにします
            server_process = subprocess.Popen([SERVER_EXECUTABLE], preexec_fn=os.setsid)
    return index()

# サーバーを停止するエンドポイント
@app.route("/stop", methods=["POST"])
def stop_server():
    global server_process
    with process_lock:
        if server_process and server_process.poll() is None:
            # プロセスグループ全体を終了させる
            os.killpg(os.getpgid(server_process.pid), 9)
            server_process.wait()
            server_process = None
    return index()

# アプリケーションの実行
if __name__ == "__main__":
    # Render環境ではPORT変数が自動で設定されるため、それを使う
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
