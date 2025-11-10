# Python 3.11 スリム版を使用
FROM python:3.11-slim

# 必要なLinuxパッケージとgdownをインストール
# gdown は、Google Driveの大きなファイルのダウンロードを助けるツールです。
RUN apt-get update && apt-get install -y wget curl gnupg && \
    pip install gdown gunicorn

# 🚨 環境変数の設定 (ファイル ID をここで指定)
ENV G_DRIVE_FILE_ID="16OlbXH73OzxJvUd80k0ARC0wAzgNm5_-"
ENV LINUX_BINARY_NAME="your_linux_app" # 実行ファイル名 (お好みで変更可)

# 作業ディレクトリの設定
WORKDIR /usr/src/app

# 1. Google Driveから100MB超のファイルをダウンロード
# ダウンロードが失敗しないよう、リンクを知っている全員が「閲覧者」以上に設定されているか再確認してください。
RUN gdown --id $G_DRIVE_FILE_ID --output $LINUX_BINARY_NAME && \
    # 2. 実行権限を付与 (Linuxで実行可能にするため必須)
    chmod +x $LINUX_BINARY_NAME

# 依存関係（Flask, gunicorn）のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY app.py .

# Flaskアプリの起動 (GunicornでWebサーバーとして公開)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
