# Python 3.11 スリム版を使用 (ベースイメージ)
FROM python:3.11-slim

# 必要なLinuxパッケージとツールをインストール
# unzip, wget はサーバーファイルをダウンロード・展開するために必要
RUN apt-get update && apt-get install -y wget curl unzip gnupg && \
    pip install gunicorn

# 🚨 環境変数の設定 (提供いただいた最新のURLを適用)
ENV BEDROCK_SERVER_URL="https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.21.121.1.zip"
ENV LINUX_BINARY_NAME="bedrock_server"

# 作業ディレクトリの設定
WORKDIR /usr/src/app

# Git リポジトリにある全てのファイル/設定をコピー
# (app.py, requirements.txt, server.properties, worlds/ など)
COPY . .

# 依存関係（Flask, gunicorn）のインストール
RUN pip install --no-cache-dir -r requirements.txt

# 1. 公式サイトから最新のサーバーZIPファイルをダウンロード
RUN wget -O bedrock_server.zip $BEDROCK_SERVER_URL && \
    # 2. ZIPファイルを解凍 (バイナリと全ての設定ファイル、データファイルが展開される)
    unzip -o bedrock_server.zip -d . && \
    # 3. ダウンロードしたZIPファイルを削除 (容量節約)
    rm bedrock_server.zip && \
    # 4. サーバーバイナリに実行権限を付与
    chmod +x $LINUX_BINARY_NAME

# Flaskアプリの起動 (GunicornでWebサーバーとして公開)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
