#!/bin/bash
# Build.sh: プロジェクトの動作環境をセットアップするスクリプト
# Usage: bash Build.sh

set -e

# PETMLとPETSQLのクローン
if [ ! -d "PETML" ]; then
  git clone https://github.com/tiktok-privacy-innovation/PETML
fi

if [ ! -d "PETSQL" ]; then
  git clone https://github.com/tiktok-privacy-innovation/PETSQL
fi

# Dockerがインストールされているか確認
if ! command -v docker &> /dev/null ; then
    echo "Dockerがインストールされていません。Dockerのインストールを試みます..."

    echo "Debian/Ubuntuを検出しました。aptを使用してDockerをインストールします..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
        "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        \"$(. /etc/os-release && echo \"$VERSION_CODENAME\")\" stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo "現在のユーザーを 'docker' グループに追加します..."
    sudo usermod -aG docker $USER
    echo "Dockerのインストールが完了しました。グループの変更を反映するには、一度ログアウトして再度ログインする必要がある場合があります。"
    echo "再ログイン後、再度 'bash build.sh' を実行してください。"
    exit 0 # インストール後に終了 (ユーザーは再ログインが必要)
fi


docker rmi -f petplatform:latest || true
docker build --no-cache -t petplatform:latest . -f docker/Dockerfile

docker rm -f petplatform || true

# スクリプトのディレクトリを絶対パスで取得
SCRIPT_DIR=$(dirname "$0")

# ボリュームマウント用のディレクトリを作成
mkdir -p "${SCRIPT_DIR}/docker/db"
mkdir -p "${SCRIPT_DIR}/docker/data"
mkdir -p "${SCRIPT_DIR}/docker/logs"

docker run -d \
  --name petplatform \
  -u 1000:1000 \
  -v "${SCRIPT_DIR}/docker/db:/app/db" \
  -v "${SCRIPT_DIR}/docker/data:/app/data" \
  -v "${SCRIPT_DIR}/docker/logs:/app/logs" \
  -v "${SCRIPT_DIR}/docker/party.json:/app/parties/party.json" \
  -e TZ=Asia/Tokyo \
  -e PARTY=party_a \
  -p 1234:1234 \
  -e SECRET='a-very-secret-key' \
  petplatform:latest

# --- JWT認証とAPIアクセスについて ---
# アプリケーションはJWT認証を使用します。APIにアクセスするには、有効なJWTトークンが必要です。
# 以下の手順でトークンを生成し、APIにアクセスできます。

# 1. JWTトークンの生成:
#    コンテナ内で initialize_jwt.py スクリプトを実行してトークンを生成します。
#    これにより、テスト用のユーザー (user_0 など) のトークンが出力されます。
docker exec petplatform python3 /app/initialize_jwt.py

# 2. 生成したトークンを使用したAPIアクセス:
#    生成されたトークンを Authorization ヘッダーに含めて API にリクエストを送信します。
#    例: GET /api/v1/jobs
#    docker exec petplatform curl -X GET -H "Authorization: Bearer <生成したトークン>" http://localhost:1234/api/v1/jobs
#    <生成したトークン> の部分を、上記手順1で取得したトークンに置き換えてください。
