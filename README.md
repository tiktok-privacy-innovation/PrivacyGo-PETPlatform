git clone https://github.com/tiktok-privacy-innovation/PETML .
# PrivacyGo-PETPlatform (Forked Project)

このリポジトリはオリジナルのPrivacyGo-PETPlatformをforkし、独自の拡張・開発を行っています。

## 本プロジェクトの主な変更点

- **セットアップ用の `build.sh` スクリプトを追加**
    - プロジェクトのセットアップやビルドを簡単に行うためのシェルスクリプト `build.sh` を作成しました。
    - 詳細は `build.sh` をご参照ください。

- **VSCode用デバッグ実行設定ファイルを追加**
    - Visual Studio Code でのデバッグ実行を容易にするため、`.vscode/launch.json` などの設定ファイルを追加しました。
    - これにより、VSCode上でサーバや主要スクリプトのデバッグが簡単に行えます。

## セットアップ手順（fork版）

### 前提

以下の環境で構築しています。

- Windows11
- WSL2 Ubuntu24.04
- VsCode + DevContainers

1. Dockerでとりあえず動かす場合
    ```bash
    bash build.sh
    ```
1. VSCodeで開発する場合
    - DevContainersでDocker開発環境を起動し、F5でAPサーバー起動

## オリジナルREADMEについて

オリジナルのREADMEは `README_ORIGINAL.md` に移動しています。プロジェクトの全体像や詳細な使い方はそちらをご参照ください。


## APIエンドポイント一覧（/src/views/v1.pyより）

### エンドポイント一覧

|No.| 種別 | URL | メソッド | 概要 |
|-|------|-----|----------|------|
|1| ジョブ新規作成 | `/api/v1/jobs` | POST | ジョブ（ミッション）を新規作成・投入 |
|2| ジョブ再実行   | `/api/v1/jobs/<job_id>/rerun` | POST | 失敗/キャンセル済みジョブの再実行 |
|3| ジョブキャンセル| `/api/v1/jobs/<job_id>/cancel` | POST | ジョブのキャンセル |
|4| ジョブ詳細取得  | `/api/v1/jobs/<job_id>` | GET | ジョブの詳細・進捗取得 |
|5| ジョブ一覧取得  | `/api/v1/jobs` | GET | ジョブの一覧取得（フィルタ可） |
|6| タスク状態更新  | `/api/v1/tasks/<job_id>/<task_name>` | PATCH | タスク状態の更新（ノード間連携用） |

各エンドポイントの詳細なパラメータやレスポンス例は、プロジェクト内の `/src/views/v1.py` を参照してください。

### 1. ジョブの新規作成
| 項目 | 内容 |
|---|---|
| **URL** | `/api/v1/jobs` |
| **Method** | `POST` |
| **認証** | JWT必須 |

**Bodyパラメータ (JSON):**

| フィールド名      | 型      | 必須 | 説明                                                        | 備考                      |
|-------------------|---------|------|-------------------------------------------------------------|---------------------------|
| mission_name      | str     | 任意 | 実行するミッション名（例: "ecdh_psi_optimized"）           | 省略時はデフォルト値      |
| mission_version   | str/int | 任意 | ミッションのバージョン（例: "latest" または数値）           | 省略時は "latest"        |
| main_party        | str     | 任意 | メインとなるパーティ名                                       | 省略時は settings.PARTY   |
| mission_params    | dict    | 任意 | ミッションごとのパラメータ（ユーザー入力値）                 | 省略時は空dict            |
| job_id            | str     | 任意 | ジョブID（指定しない場合は自動生成）                         | 通常は省略でOK            |

> `mission_params` の中身はミッション（アルゴリズム）ごとに異なります。例: PSIなら入力ファイルパスや出力先パス、XGBoostなら特徴量やラベル名など。

### 2. ジョブ再実行
### 3. ジョブキャンセル
### 4. ジジョブ詳細取得
### 5. ジョブ一覧取得

| 項目 | 内容 |
|---|---|
| **URL** | `/api/v1/jobs` |
| **Method** | `GET` |
| **認証** | JWT必須 |
| **クエリパラメータ** | `status` (任意): ジョブの状態<br>`hours` (任意): 何時間以内のジョブを取得するか<br>`limit` (任意): 最大取得件数（デフォルト10） |

**レスポンス例:**
```json
{
    "success": true,
    "jobs": [
        { "job_id": "xxxx", "status": "SUCC" },
        { "job_id": "yyyy", "status": "RUNN" }
    ]
}
```

### 6. タスク状態更新
| 項目 | 内容 |
|---|---|
| **URL** | `/api/v1/tasks/<job_id>/<task_name>` |
| **Method** | `PATCH` |
| **認証** | JWT必須（ノード認証） |
| **パスパラメータ** | `job_id`: 対象ジョブID<br>`task_name`: 対象タスク名 |

**Bodyパラメータ (JSON):**

| フィールド名   | 型   | 必須 | 説明                     |
|---------------|------|------|--------------------------|
| task_status   | str  | 必須 | 新しいタスク状態         |
| job_context   | dict | 任意 | タスクの追加情報         |
| errors        | str  | 任意 | エラー情報（失敗時のみ） |

**レスポンス例:**
```json
{ "success": true }
```



---

---
各APIはすべてJWT認証が必要です。詳細なパラメータやレスポンスは実装や運用環境により異なる場合があります。


## API利用例

### 1. PSIミッションで共通IDを抽出

#### ジョブ投入用JSON例（APIリクエスト例）
```json
{
  "mission_name": "psi",
  "mission_version": "latest",
  "main_party": "party_a",
  "mission_params": {
    "input_path": "/data/purchase.csv",      // 広告主の購買データ
    "partner_input_path": "/data/exposure.csv", // 媒体主の広告接触データ
    "output_path": "/data/psi_result.csv",   // 共通ユーザー出力先
    "id_column": "user_id"                   // 突合に使うカラム名
  }
}
```

#### cURLコマンド例
```bash
curl -X POST \
    -H "Authorization: Bearer <JWT_TOKEN>" \
    -H "Content-Type: application/json" \
    -d @psi_job.json \
    http://localhost:1234/api/v1/jobs
```
※ `psi_job.json` に上記JSONを保存し、<JWT_TOKEN> を自身のトークンに置き換えてください。

#### 入力CSVファイル例

- 広告主（party_a）の購買データ `/data/purchase.csv`
  ```csv
  user_id,amount
  A001,1200
  A002,800
  A003,1500
  A004,600
  ```

- 媒体主（party_b）の広告接触データ `/data/exposure.csv`
  ```csv
  user_id,ad_id
  A002,AD10
  A003,AD11
  A005,AD12
  ```

#### ミッションの出力例（共通ユーザー）

- `/data/psi_result.csv`
    ```csv
    user_id
    A002
    A003
    ```

### 2. SQLミッションで両者のデータをJOIN

#### ジョブ投入用JSON例（APIリクエスト例）
```json
{
    "mission_name": "sql",
    "mission_version": "latest",
    "main_party": "party_a",
    "mission_params": {
        "sql": "SELECT a.user_id, a.amount, b.ad_id FROM a INNER JOIN b ON a.user_id = b.user_id",
        "input_path_a": "/data/purchase.csv",
        "input_path_b": "/data/exposure.csv",
        "output_path": "/data/joined_result.csv"
  }
}
```

#### cURLコマンド例
```bash
JWT_TOKEN=＜python3 src/initialize_jwt.pyで生成したJWTトークン＞
curl -X POST \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d @sql_job.json \
    http://localhost:1234/api/v1/jobs
```
※ `sql_job.json` に上記JSONを保存し、<JWT_TOKEN> を自身のトークンに置き換えてください。

#### 入力CSVファイル例

- 広告主（party_a）の購買データ `/data/purchase.csv`
    ```csv
    user_id,amount
    A001,1200
    A002,800
    A003,1500
    A004,600
    ```

- 媒体主（party_b）の広告接触データ `/data/exposure.csv`
    ```csv
    user_id,ad_id
    A002,AD10
    A003,AD11
    A005,AD12
    ```

#### ミッションの出力例
```csv
user_id,amount,ad_id
A002,800,AD10
A003,1500,AD11
```
