import subprocess
from flask import Flask, render_template_string
import os

# Flaskアプリケーションの初期化
app = Flask(__name__)
print(f"app:{app}")

# 🚨 Linuxバイナリのファイル名 (このファイルをプロジェクトフォルダに置いてください)
LINUX_BINARY_NAME = "bedrock_server" 
print(f"LINUX_BINARY_NAME:{LINUX_BINARY_NAME}")

# バイナリファイルの実行パスを設定
# コンテナまたは実行環境のルートにある想定
EXECUTABLE_PATH = f"./{LINUX_BINARY_NAME}"
print(f"EXECUTABLE_PATH:{EXECUTABLE_PATH}")

# ホームページ
@app.route('/')
def index():
    html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>Linuxバイナリ実行アプリ</title>
        <style>
            body {{ font-family: sans-serif; text-align: center; margin-top: 50px; }}
            button {{ padding: 10px 20px; font-size: 18px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>Linuxバイナリ実行アプリ</h1>
        <p>下のボタンを押すと、クラウドサーバー上で {LINUX_BINARY_NAME} が実行されます。</p>
        <form action="/run_app" method="post">
            <button type="submit">🚀 Linuxアプリを実行する</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(html)

# Linuxバイナリ実行エンド
# app.py の run_app 関数を以下に置き換えてください。

@app.route('/run_app', methods=['POST'])
def run_app():
    # 実行ファイルのパス
    EXECUTABLE_PATH = f"./{LINUX_BINARY_NAME}"
    
    try:
        os.chmod(EXECUTABLE_PATH, 0o755)
    except Exception as e:
        print(f"chmod error: {e}") 

    try:
        # 🚨 修正点: subprocess.run を subprocess.Popen に変更！
        # Popen はプロセスをバックグラウンドで起動し、すぐに制御を返します。
        # Web アプリはフリーズしません。
        
        # サーバーの標準出力/エラー出力を無視して、親プロセス (Flask) にブロックされないようにします。
        # ログを確認したい場合は、ファイルにリダイレクトするなどの工夫が必要です。
        
        process = subprocess.Popen(
            [EXECUTABLE_PATH], 
            # サーバーの出力を捨てることで、Pipeが詰まるのを防ぎます
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            # Render の環境では、シェルを使わない方がクリーンです
            # shell=False 
        )

        print(f"マイクラ Bedrock サーバーを PID: {process.pid} でバックグラウンド起動しました！")
        
        # 起動成功のレスポンスを即座に返す
        return f'<h2>✅ サーバーをバックグラウンドで起動しました！</h2><p>Renderはサーバー実行専用ではないため、起動直後に落ちる可能性もありますが、まずは接続を試みてください。</p><p>プロセスID: {process.pid}</p><p><a href="/">戻る</a></p>'
    
    except Exception as e:
        print(f"サーバー起動中にエラーが発生しました: {e}")
        return f'<h2>❌ サーバー起動中にエラーが発生しました。</h2><p>Python例外: {e}</p><p><a href="/">戻る</a></p>'
