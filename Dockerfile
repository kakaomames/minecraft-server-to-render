# Python 3.11 スリム版を使用
FROM python:3.11-slim

# 必要なLinuxパッケージとgdownをインストール
# tar や gzip は不要になりました
RUN apt-get update && apt-get install -y wget curl gnupg && \
    pip install gdown gunicorn

# 🚨 環境変数の設定
ENV G_DRIVE_FILE_ID="16OlbXH73OzxJvUd80k0ARC0wAzgNm5_-" # bedrock_serverのファイルID
ENV LINUX_BINARY_NAME="bedrock_server" # サーバーのバイナリ名はこれに固定します

# 作業ディレクトリの設定
WORKDIR /usr/src/app

# 依存関係とアプリケーションコード、設定ファイルをコピー
# この時点で、server.properties などの設定ファイルもコンテナにコピーされます
COPY requirements.txt .
COPY app.py .
# 🚨 その他、server.properties, permissions.json, worlds フォルダなどを全てコピー
# Git リポジトリにあるすべてのファイル/フォルダがここにコピーされます。
COPY . .

# 依存関係（Flask, gunicorn）のインストール
RUN pip install --no-cache-dir -r requirements.txt

# 1. Google Driveから100MB超のバイナリをダウンロード
# ダウンロードしたファイルは作業ディレクトリに保存されます
RUN gdown --id $G_DRIVE_FILE_ID --output $LINUX_BINARY_NAME && \
    # 2. 実行権限を付与 (Linuxで実行可能にするため必須)
    chmod +x $LINUX_BINARY_NAME

# Flaskアプリの起動 (GunicornでWebサーバーとして公開)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
