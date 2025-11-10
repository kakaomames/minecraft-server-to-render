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
# app.py 内の run_app 関数を以下に置き換えてください。

@app.route('/run_app', methods=['POST'])
def run_app():
    # 実行ファイルのパス (Dockerfileで設定した LINUX_BINARY_NAME と一致しているか再確認)
    EXECUTABLE_PATH = f"./{LINUX_BINARY_NAME}"
    
    # 実行権限を念のため付与 (Render環境では一度設定しても失われる可能性があるため)
    try:
        os.chmod(EXECUTABLE_PATH, 0o755)
        print("実行権限を付与しました。")
    except Exception as e:
        # chmodに失敗しても続行
        print(f"chmod error: {e}") 

    try:
        # 🚨 タイムアウトを60秒に延長 (100MB超のアプリは起動に時間がかかるため)
        # 🚨 check=False にし、戻り値が非ゼロでもエラー画面に詳細を表示させる
        result = subprocess.run(
            [EXECUTABLE_PATH], 
            capture_output=True, 
            text=True, 
            check=False, # 戻り値が非ゼロでも例外にせず、詳細を出力
            timeout=60 # 60秒に延長
        )

        stdout = result.stdout
        stderr = result.stderr
        return_code = result.returncode

        print(f"アプリの実行が完了しました。戻り値: {return_code}")
        print(f"stdout:\n{stdout}")
        print(f"stderr:\n{stderr}")
        
        # 実行結果を詳細に表示するHTMLを返す
        html_output = f"""
        <h2>✅ 実行結果 ({'成功' if return_code == 0 else '失敗'})</h2>
        <p>戻り値: {return_code}</p>
        
        <h3>標準出力 (stdout):</h3>
        <pre style="background-color: #eee; padding: 10px;">{stdout}</pre>
        
        <h3>標準エラー出力 (stderr):</h3>
        <pre style="background-color: #fee; padding: 10px;">{stderr}</pre>
        
        <p><a href="/">戻る</a></p>
        """
        return render_template_string(html_output)
    
    except subprocess.TimeoutExpired:
        print("アプリが時間内に応答しませんでした。")
        return '<h2>❌ アプリの実行がタイムアウトしました。</h2><p>アプリケーションが60秒以内に終了しませんでした。</p><p><a href="/">戻る</a></p>'
    
    except Exception as e:
        print(f"実行中に予期せぬエラーが発生しました: {e}")
        return f'<h2>❌ 実行中に予期せぬエラーが発生しました。</h2><p>Python例外: {e}</p><p><a href="/">戻る</a></p>'
