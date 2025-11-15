# 🚨 最終修正: 公式の非推奨タグを避け、推奨される代替イメージ Eclipse Temurin (JRE 17) を使用
# 'jre' (実行環境) と 'focal' (安定したUbuntuベース) を選択
FROM eclipse-temurin:21-jre-focal 

# 必要なパッケージをインストール (Temurin イメージは slim なので wget/curl を追加)
# Renderのビルド環境では、apt-get update が必須
RUN apt-get update && apt-get install -y wget curl

# 🚨 環境変数の設定 (ダウンロードURLを適用)
# 1. Java版サーバー (公式URL)
ENV VANILLA_SERVER_URL="https://piston-data.mojang.com/v1/objects/95495a7f485eedd84ce928cef5e223b757d2f764/server.jar"
# 2. GeyserMC Standalone の最新URL 
ENV GEYSER_URL="https://download.geysermc.org/v2/projects/geyser/versions/latest/builds/latest/downloads/standalone" 

ENV SERVER_JAR_NAME="minecraft_server.jar"
ENV GEYSER_JAR_NAME="Geyser-Standalone.jar"

# 作業ディレクトリの設定
WORKDIR /usr/src/app

# 1. Java版サーバーとGeyserMCをダウンロード
# 安定性の高い公式URLを使用
RUN wget -O $SERVER_JAR_NAME $VANILLA_SERVER_URL && \
    wget -O $GEYSER_JAR_NAME $GEYSER_URL

# 2. EULAファイルを作成 (Minecraftサーバー起動に必須)
RUN echo "eula=true" > eula.txt

# 3. GeyserMCの設定ファイルを作成
RUN mkdir -p GeyserMC && \
    echo "bedrock: \n  port: 5000 \n  address: 0.0.0.0 \nremote: \n  address: 127.0.0.1 \n  port: 25565" > GeyserMC/config.yml

# 4. サーバー起動用のラッパースクリプトをコピー
COPY start.sh .
RUN chmod +x start.sh

# 5. サーバー起動
CMD ["./start.sh"]
