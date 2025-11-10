import subprocess
from flask import Flask, render_template_string
import os

# Flaskアプリケーションの初期化
app = Flask(__name__)
print(f"app:{app}")

# 🚨 Linuxバイナリのファイル名 (このファイルをプロジェクトフォルダに置いてください)
LINUX_BINARY_NAME = "your_linux_app" 
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

# Linuxバイナリ実行エンドポイント
@app.route('/run_app', methods=['POST'])
def run_app():
    # 実行権限を念のため付与 (デプロイ環境で実行権限がない場合があるため)
    try:
        os.chmod(EXECUTABLE_PATH, 0o755)
    except Exception as e:
        print(f"chmod error: {e}")

    try:
        # 実行可能であることを確認
        if not os.path.exists(EXECUTABLE_PATH):
            return f'<h2>❌ エラー: 実行ファイルが見つかりません。</h2><p>パス: <code>{EXECUTABLE_PATH}</code></p><p><a href="/">戻る</a></p>'
        
        # subprocess.run を使用して実行し、標準出力を取得
        # shell=Trueはセキュリティリスクがあるため、推奨しません。
        # ここでは、出力を待って成功/失敗を判定します。
        
        # 🚨 補足: 100MB超のアプリが長時間実行される場合、タイムアウトに注意が必要です。
        # RenderやVercelでは、応答に時間がかかりすぎると接続が切断されます。
        
        result = subprocess.run(
            [EXECUTABLE_PATH], 
            capture_output=True, 
            text=True, 
            check=True, # 戻り値が非ゼロの場合にCalledProcessErrorを発生させる
            timeout=30 # 実行タイムアウト（必要に応じて調整）
        )

        output = result.stdout
        print(f"アプリの実行が完了しました。出力:\n{output}")
        
        # 実行成功メッセージとアプリの出力を表示
        return f'<h2>✅ Linuxアプリの実行が完了しました！</h2><p>アプリケーションからの出力:</p><pre>{output}</pre><p><a href="/">戻る</a></p>'
    
    except subprocess.CalledProcessError as e:
        print(f"アプリの実行中にエラーが発生しました: {e.stderr}")
        return f'<h2>❌ アプリの実行エラーが発生しました。</h2><p>標準エラー出力: {e.stderr}</p><p><a href="/">戻る</a></p>'
    
    except subprocess.TimeoutExpired:
        print("アプリが時間内に応答しませんでした。")
        return f'<h2>❌ アプリの実行がタイムアウトしました。</h2><p>アプリケーションが30秒以内に終了しませんでした。長時間処理の場合は、非同期処理を検討してください。</p><p><a href="/">戻る</a></p>'

# GunicornなどWebサーバーの起動に対応するため、__name__ == '__main__'ブロックは削除します。
# デプロイ環境ではGunicornがWSGIを呼び出すため、ローカル実行が必要な場合のみ以下を追加してください。
# if __name__ == '__main__':
#     app.run(debug=True, port=5000)
