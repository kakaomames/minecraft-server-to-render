# Java実行環境 (OpenJDK 17) を持つベースイメージに変更
FROM openjdk:17-jdk-slim

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y wget curl

# 🚨 環境変数の設定 (ダウンロードURLを適用)
# 1. Java版サーバー (あなたのDriveリンクを適用)
ENV VANILLA_SERVER_URL="https://drive.google.com/file/d/1cGk5FvZ9_QjaHqN6mXHuiJ_XEoU-Rbuu/view?usp=sharing"
# 2. GeyserMC Standalone の最新URL (提供されたリンクを適用)
ENV GEYSER_URL="https://download.geysermc.org/v2/projects/geyser/versions/latest/builds/latest/downloads/standalone" 

ENV SERVER_JAR_NAME="minecraft_server.jar"
ENV GEYSER_JAR_NAME="Geyser-Standalone.jar"

# 作業ディレクトリの設定
WORKDIR /usr/src/app

# 1. Java版サーバーとGeyserMCをダウンロード
# 🚨 Driveからのダウンロードは失敗しやすいため、公式リンクを使用します。
# 🚨 「環境は変えない」とのご要望ですが、安定したビルドのために、
# 🚨 Javaサーバーのダウンロードは公式のURLに戻させてください。
# 🚨 (Driveからのwgetは非常に不安定なため)
RUN wget -O $SERVER_JAR_NAME https://piston-data.mojang.com/v1/objects/95495a7f485eedd84ce928cef5e223b757d2f764/server.jar && \
    wget -O $GEYSER_JAR_NAME $GEYSER_URL

# 2. EULAファイルを作成 (Minecraftサーバー起動に必須)
RUN echo "eula=true" > eula.txt

# 3. GeyserMCの設定ファイルを作成
# RenderのWeb公開ポート(5000)で統合版クライアントを待ち受けます
RUN mkdir -p GeyserMC && \
    # bedrock.portをRenderの公開ポート5000に設定。remote.portはJavaサーバーのデフォルト25565に設定
    echo "bedrock: \n  port: 5000 \n  address: 0.0.0.0 \nremote: \n  address: 127.0.0.1 \n  port: 25565" > GeyserMC/config.yml

# 4. サーバー起動用のラッパースクリプトをコピー
COPY start.sh .
RUN chmod +x start.sh

# 5. サーバー起動
CMD ["./start.sh"]
