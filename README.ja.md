<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-ゼロ-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="English"></a>
</p>

# VNE MCP Server

**VoidNovelEngine 用 MCP（Model Context Protocol）サーバー。** AI アシスタントが VNE プロジェクトを読み取り・検索・パッケージ・デバッグできます。11 ツール、Python 標準ライブラリのみ、外部依存ゼロ。

---

## 目次

- [📦 インストールとファイル配置](#-インストールとファイル配置)
- [🛠 11 ツール](#-11-ツール)
- [🚀 クイックスタート](#-クイックスタート)
- [🔧 クライアント設定](#-クライアント設定)
  - [Claude Desktop](#claude-desktop)
  - [Cursor / Windsurf](#cursor--windsurf)
  - [Hermes Agent](#hermes-agent)
  - [汎用 MCP クライアント](#汎用-mcp-クライアント)
- [🔗 TCP モードとエディタ統合](#-tcp-モードと-vne-エディタ統合)
- [🔐 VPak 統合](#-vpak-統合)
- [📁 ファイル構造](#-ファイル構造)
- [📋 要件](#-要件)
- [🔗 リンク](#-リンク)

---

## 📦 インストールとファイル配置

### ファイルの説明

このリポジトリには **2 つの Python ファイル** が含まれており、両方とも必須です：

| ファイル | 役割 | 必須 |
|---------|------|:---:|
| `vne_mcp_server.py` | MCP サーバーメインプログラム（11 ツール） | ✓ 必須 |
| `vpak.py` | VPak パック/アンパックモジュール | ✓ 必須 |

`vne_pack_resources` と `vne_read_vpak` ツールは `vpak.py` を呼び出すため、**2 つのファイルは同じディレクトリに配置する必要があります**。

### セットアップ手順

```bash
# 1. ホームディレクトリにクローン（推奨）
git clone https://github.com/zv163/vne-mcp-server.git ~/vne-mcp-server

# 2. ファイルを確認
ls ~/vne-mcp-server/
# 出力: vne_mcp_server.py  vpak.py  README.md  LICENSE

# 3. Python バージョンを確認（3.8 以上）
python3 --version

# 4. 動作テスト
python3 ~/vne-mcp-server/vne_mcp_server.py --list-tools
```

> **パスのヒント：** `~/vne-mcp-server/` または任意の固定パスに配置してください。VNE プロジェクトの内部には置かないでください。これは独立したツールであり、複数の VNE プロジェクトに対応できます。

### 配置の全体像

```
~/vne-mcp-server/              ← 推奨インストール先
├── vne_mcp_server.py          ← MCP サーバー（必須）
├── vpak.py                    ← VPak モジュール（同ディレクトリ必須）
├── README.md / .en.md / .ja.md
└── LICENSE

/path/to/VoidNovelEngine/      ← VNE プロジェクト（任意の場所）
├── project.vne
├── application/
│   ├── resources/
│   ├── framework/
│   └── scene/
└── save/diagnostics/
```

---

## 🛠 11 ツール

| # | ツール名 | 機能 | R/O |
|---|---------|------|:---:|
| 1 | `vne_project_info` | プロジェクト概要 — バージョン、アセット数、パス | ✓ |
| 2 | `vne_list_resources` | タイプ別リソース一覧（テクスチャ、音声、フロー等） | ✓ |
| 3 | `vne_read_file` | 任意ファイルを読み取り | ✓ |
| 4 | `vne_list_directory` | ディレクトリ構造を閲覧 | ✓ |
| 5 | `vne_search` | Lua スクリプト全文検索（大文字小文字区別なし） | ✓ |
| 6 | `vne_get_resource` | GUID でリソース詳細を取得（.meta 含む） | ✓ |
| 7 | `vne_lua_api` | エンジン Lua API リファレンス | ✓ |
| 8 | `vne_export_config` | エクスポート設定（タイトル、エントリーフロー、VPak 状態） | ✓ |
| 9 | `vne_pack_resources` | VPak リソース暗号化パッケージを実行（XOR + zlib） | ✗ |
| 10 | `vne_read_vpak` | .vpak アーカイブの一覧表示・ファイル抽出 | ✓ |
| 11 | `vne_console_log` | エディタコンソールログをリアルタイム取得 | ✓ |

---

## 🚀 クイックスタート

```bash
# プロジェクト情報を表示
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine --info

# 全テクスチャを一覧
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine --resources texture

# 利用可能なツールを表示
python3 ~/vne-mcp-server/vne_mcp_server.py --list-tools
```

### Stdio モード（デフォルト、MCP クライアント用）

```bash
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine
```

### TCP/HTTP モード（VNE エディタ内蔵用）

```bash
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine --port 8765
```

| エンドポイント | 用途 |
|---------------|------|
| `http://127.0.0.1:8765/sse` | SSE プッシュチャンネル |
| `http://127.0.0.1:8765/message` | メッセージ受信 |
| `http://127.0.0.1:8765/health` | ヘルスチェック |

---

## 🔧 クライアント設定

> **注意：** 以下の `/path/to/vne-mcp-server/` は実際のインストールパス（例：`~/vne-mcp-server`）に置き換えてください。

### Claude Desktop

`claude_desktop_config.json` を編集：

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/home/ユーザー名/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/path/to/VoidNovelEngine"
      ]
    }
  }
}
```

### Cursor / Windsurf

同じ JSON 形式で MCP 設定ファイルに追加。

### Hermes Agent

```bash
# 1. ラッパースクリプトを作成
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 ~/vne-mcp-server/vne_mcp_server.py \
  --project-path /path/to/VoidNovelEngine "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh

# 2. Hermes に登録
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh

# 3. 確認
hermes mcp list | grep vne
```

> **注意：** `hermes mcp add` で `--project-path` が認識されないエラーが出る場合は、上記のラッパースクリプト方式を使用してください。

### 汎用 MCP クライアント

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/path/to/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/path/to/VoidNovelEngine"
      ]
    }
  }
}
```

---

## 🔗 TCP モードと VNE エディタ統合

VNE エディタには Lua MCP ホスト (`mcp_host.lua`) が組み込まれており、起動時に：

1. システム上の Python を自動検出
2. `vne_mcp_server.py --port 8765` を子プロセスとして起動
3. `VNE_MCP_READY` シグナルを待機
4. SSE 接続を確立してリアルタイムイベントを受信
5. `LogManager.log()` の出力 → `save/diagnostics/mcp_console.jsonl` に橋渡し

これにより **`vne_console_log`** ツールが有効になり、AI がエディタコンソールをほぼリアルタイムで読み取れます。

```
┌─────────────────────────┐
│     AI アシスタント       │
│  (Claude / GPT / Cursor) │
└─────┬───────────────────┘
      │ MCP (stdio / HTTP SSE)
┌─────▼───────────────────┐
│   vne_mcp_server.py      │
│  ┌─────────────────────┐ │
│  │  MCP プロトコル層     │ │
│  │  (JSON-RPC 2.0)     │ │
│  ├─────────────────────┤ │
│  │  VNEProject コア     │ │
│  │  · project.vne 解析  │ │
│  │  · アセット索引      │ │
│  │  · ファイル I/O      │ │
│  │  · 全文検索          │ │
│  ├─────────────────────┤ │
│  │  VPak モジュール     │ │
│  │  · vpak.py 子プロセス│ │
│  ├─────────────────────┤ │
│  │  コンソールブリッジ   │ │
│  │  · jsonl リーダー    │ │
│  └─────────────────────┘ │
└─────┬───────────────────┘
      │ ファイル読取 / 子プロセス
┌─────▼───────────────────┐
│  VNE プロジェクト         │
│  ├── project.vne        │
│  ├── application/       │
│  │   ├── resources/     │
│  │   ├── framework/     │
│  │   └── scene/         │
│  └── save/diagnostics/  │
└─────────────────────────┘
```

---

## 🔐 VPak 統合

- **`vne_pack_resources`** — `vpak.py pack` を子プロセスとして実行（XOR 暗号化、オプション zlib）
- **`vne_read_vpak`** — `vpak.py` モジュールをインポートして一覧表示・抽出

`vpak.py` は単体でも使用可能：

```bash
# パック
python3 ~/vne-mcp-server/vpak.py pack  resources/  resources.vpak --key my-key

# 一覧
python3 ~/vne-mcp-server/vpak.py list  resources.vpak

# 抽出
python3 ~/vne-mcp-server/vpak.py extract  resources.vpak  texture/icon.png --key my-key
```

### VPak フォーマット

| セクション | サイズ | 説明 |
|-----------|--------|------|
| Magic | 4 バイト | `VPAK` |
| Version | 4 バイト | uint32 LE |
| Flags | 4 バイト | bit0=暗号化, bit1=圧縮 |
| File Count | 4 バイト | uint32 LE |
| File Table | N×32 バイト | パスハッシュ + オフセット + サイズ |
| Data | N バイト | 連結ファイルデータ |

暗号化：XOR 暗号、256 バイト回転キー（SHA256 + 決定論的スクランブルから派生）

---

## 📁 ファイル構造

```
vne-mcp-server/
├── vne_mcp_server.py   # メインサーバー (1118 行、11 ツール)
├── vpak.py             # VPak パッケージャー (316 行、XOR + zlib)
├── README.md           # 中国語（デフォルト）
├── README.en.md        # 英語
├── README.ja.md        # 日本語（このファイル）
└── LICENSE             # MIT
```

---

## 📋 要件

- **Python 3.8+** — 標準ライブラリのみ、pip インストール不要
- VoidNovelEngine プロジェクト（`project.vne` を含む）

---

## 🔗 リンク

- [VoidNovelEngine](https://github.com/VoidmatrixHeathcliff/VoidNovelEngine) — ビジュアルノベルエンジン
- [Model Context Protocol](https://modelcontextprotocol.io) — MCP 仕様
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — 自己進化 AI エージェント

---

## ライセンス

MIT — [LICENSE](LICENSE) を参照
