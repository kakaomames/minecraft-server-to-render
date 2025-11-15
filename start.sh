#!/bin/bash

# Java版サーバーをバックグラウンドで起動
# メモリ設定を1024Mに固定
echo "Starting Minecraft Java Server (1.21.10) in background..."
java -Xmx1024M -Xms1024M -jar minecraft_server.jar nogui & 
JAVA_PID=$! # プロセスIDを保存

# サーバー起動を待機 (Javaサーバーが完全に立ち上がるまで待つ)
sleep 30 

# Geyserをメインプロセスとして起動し、Renderの公開ポート5000を使用
echo "Starting Geyser-Standalone on port 5000..."
# Geyserはconfig.ymlでポート5000を使用するように設定済み
java -jar Geyser-Standalone.jar

# Geyserが終了したら、コンテナが終了しないように監視
wait
