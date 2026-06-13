<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-ゼロ-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="English"></a>
</p>

# VNE MCP Server

**VoidNovelEngine 用 MCP（Model Context Protocol）サーバー。** AI アシスタント（Claude、GPT、Cursor など）が VNE プロジェクトを直接読み取り、検索、パッケージ、デバッグできるようにします。11 ツール、Python 標準ライブラリのみ、外部依存ゼロ。

2 つの転送モード：**Stdio**（Claude Desktop / Cursor 用）と **TCP/HTTP SSE**（VNE エディタ内蔵用）。

---

## 11 ツール

| # | ツール名 | 機能 | R/O |
|---|---------|------|:---:|
| 1 | `vne_project_info` | プロジェクト概要 — バージョン、アセット数、パス | ✓ |
| 2 | `vne_list_resources` | タイプ別リソース一覧（テクスチャ、音声、フロー等） | ✓ |
| 3 | `vne_read_file` | プロジェクト内の任意ファイルを読み取り | ✓ |
| 4 | `vne_list_directory` | ディレクトリ構造を閲覧 | ✓ |
| 5 | `vne_search` | Lua スクリプト内全文検索（大文字小文字区別なし） | ✓ |
| 6 | `vne_get_resource` | GUID でリソース詳細を取得（.meta 含む） | ✓ |
| 7 | `vne_lua_api` | エンジン Lua API リファレンス — モジュール、クラス、リソース型 | ✓ |
| 8 | `vne_export_config` | エクスポート設定 — タイトル、エントリーフロー、VPak 状態 | ✓ |
| 9 | `vne_pack_resources` | VPak リソース暗号化パッケージを実行（XOR + zlib） | ✗ |
| 10 | `vne_read_vpak` | .vpak アーカイブの一覧表示・ファイル抽出 | ✓ |
| 11 | `vne_console_log` | VNE エディタのコンソールログをリアルタイム取得 | ✓ |

---

## クイックスタート

```bash
# テスト：プロジェクト情報を表示
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine --info

# テスト：全テクスチャを一覧
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine --resources texture

# テスト：利用可能なツールを表示
python vne_mcp_server.py --list-tools
```

### Stdio モード（デフォルト）

```bash
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine
```

### TCP/HTTP モード（VNE エディタ内蔵）

```bash
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine --port 8765
```

起動後のエンドポイント：

| エンドポイント | 用途 |
|---------------|------|
| `http://127.0.0.1:8765/sse` | SSE プッシュチャンネル |
| `http://127.0.0.1:8765/message` | メッセージ受信 |
| `http://127.0.0.1:8765/health` | ヘルスチェック |

---

## クライアント設定

### Claude Desktop

`claude_desktop_config.json` を編集：

```json
{
  "mcpServers": {
    "vne": {
      "command": "python",
      "args": [
        "/path/to/vne-mcp-server/vne_mcp_server.py",
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
# ラッパースクリプトを作成
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 /path/to/vne-mcp-server/vne_mcp_server.py \
  --project-path /path/to/VoidNovelEngine "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh

# Hermes に登録
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh
```

### 汎用 MCP クライアント

```json
{
  "mcpServers": {
    "vne": {
      "command": "python",
      "args": ["vne_mcp_server.py", "--project-path", "/path/to/VoidNovelEngine"]
    }
  }
}
```

---

## TCP モードと VNE エディタ統合

VNE エディタには Lua MCP ホスト (`mcp_host.lua`) が組み込まれており、起動時に：

1. Windows 上の Python を自動検出
2. `vne_mcp_server.py --port 8765` を子プロセスとして起動
3. stdout で `VNE_MCP_READY` シグナルを待機
4. SSE 接続を確立してリアルタイムイベントを受信
5. `LogManager.log()` の出力 → `save/diagnostics/mcp_console.jsonl` に橋渡し

これにより **`vne_console_log`** ツールが有効になり、AI アシスタントが VNE エディタのコンソールをほぼリアルタイムで読み取れます。

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

## VPak 統合

2 つのツールが VPak 暗号化アーカイブと連携します：

- **`vne_pack_resources`** — `vpak.py pack` を子プロセスとして実行（XOR 暗号化、オプション zlib）
- **`vne_read_vpak`** — `vpak.py` モジュールを直接インポートして一覧表示・抽出

`vpak.py` は単体でも使用可能：

```bash
# リソースをパック
python vpak.py pack application/resources application/resources.vpak --key my-key

# アーカイブ内容を一覧
python vpak.py list application/resources.vpak

# ファイルを抽出
python vpak.py extract application/resources.vpak texture/icon.png --key my-key
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

## ファイル構造

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

## 要件

- **Python 3.8+** — 標準ライブラリのみ、pip インストール不要
- VoidNovelEngine プロジェクト（`project.vne` を含む）

---

## リンク

- [VoidNovelEngine](https://github.com/VoidmatrixHeathcliff/VoidNovelEngine) — ビジュアルノベルエンジン
- [Model Context Protocol](https://modelcontextprotocol.io) — MCP 仕様
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — 自己進化 AI エージェント

---

## ライセンス

MIT — [LICENSE](LICENSE) を参照
