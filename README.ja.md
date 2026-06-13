<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/Version-1.2.0-purple?style=for-the-badge" alt="v1.2.0">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-ゼロ依存-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="English"></a>
</p>

# VNE MCP Server

VoidNovelEngine 用 MCP サーバー。**15 ツール**、Python 標準ライブラリのみ、ゼロ依存。

AI アシスタントがプロジェクトの読み取り、コード検索、アセット管理、フロー検証、コンソールログ監視を行えます。

---

## インストール

`tools/` ディレクトリを VNE プロジェクトのルートにコピー：

```
VoidNovelEngine/
├── project.vne
├── application/
├── tools/                        ← ここに配置
│   ├── vne-mcp-server/
│   │   └── vne_mcp_server.py     ← MCP サーバー
│   └── vne-packager/
│       └── vpak.py               ← VPak パッケージャ
└── ...
```

```bash
git clone https://github.com/zv163/vne-mcp-server.git
cp -r vne-mcp-server/tools/ /path/to/your/VNE-project/
```

テスト：

```bash
python3 tools/vne-mcp-server/vne_mcp_server.py --info
python3 tools/vne-mcp-server/vne_mcp_server.py --list-tools
```

---

## 15 ツール

| # | ツール | 機能 | R/O | バージョン |
|---|--------|------|:--:|:--:|
| 1 | `vne_project_info` | プロジェクト情報、アセット統計 | ✓ | 1.0 |
| 2 | `vne_list_resources` | タイプ別リソース一覧 | ✓ | 1.0 |
| 3 | `vne_read_file` | ファイル読み取り | ✓ | 1.0 |
| 4 | `vne_list_directory` | ディレクトリ閲覧 | ✓ | 1.0 |
| 5 | `vne_search` | Lua スクリプト全文検索 | ✓ | 1.0 |
| 6 | `vne_get_resource` | リソース詳細 (.meta含む) | ✓ | 1.0 |
| 7 | `vne_lua_api` | エンジン Lua API リファレンス | ✓ | 1.0 |
| 8 | `vne_export_config` | エクスポート設定 | ✓ | 1.0 |
| 9 | `vne_pack_resources` | VPak 暗号化パッケージ実行 | ✗ | 1.0 |
| 10 | `vne_read_vpak` | .vpak アーカイブ一覧/抽出 | ✓ | 1.0 |
| 11 | `vne_console_log` | リアルタイムコンソールログ | ✓ | 1.1 |
| 12 | `vne_refresh_assets` | キャッシュリフレッシュ（再起動不要） | ✗ | **1.2** |
| 13 | `vne_register_asset` | アセット自動登録 | ✗ | **1.2** |
| 14 | `vne_validate_flow` | .flow 検証（クラッシュ防止） | ✓ | **1.2** |
| 15 | `vne_list_node_types` | 全フローノードタイプとピン定義 | ✓ | **1.2** |

---

## v1.2.0 新機能

### 1. エンジン再起動不要

.vns/.flow ファイルを外部作成後、認識させるにはエンジン再起動が必要でした。

→ `vne_refresh_assets` が内部キャッシュをクリアし、project.vne を再読み込みします。

### 2. 安全なアセット登録

project.vne の JSON を手動編集してアセット登録するのはミスが起きやすいです。

→ `vne_register_asset` が .meta 作成＋project.vne 更新をアトミックに実行。

### 3. フロークラッシュ防止

手作りの .flow JSON はピンキーが間違っていることが多く（例：`route_1` ではなく `choice_1`）、VNE エディタがクラッシュします。

→ `vne_validate_flow` が JSON 構造、ピンキー、リンク整合性をチェック。**生成した .flow を開く前に必ず呼び出してください。**
→ `vne_list_node_types` が 70 以上のノードタイプの正確なピンスキーマを表示。

### 推奨ワークフロー

```
1. vne_list_node_types     → 利用可能なノードとピン名を確認
2. .flow ファイル生成      → Python スクリプトなどで
3. vne_validate_flow       → エラーなしを確認
4. vne_register_asset      → プロジェクトに自動登録
5. vne_refresh_assets      → キャッシュをリフレッシュ
6. VNE エディタで開く      → 安全に
```

---

## クライアント設定

### Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/path/to/VNE-project/tools/vne-mcp-server/vne_mcp_server.py",
        "--project-path", "/path/to/VNE-project"
      ]
    }
  }
}
```

---

## VPak

```bash
python3 tools/vne-packager/vpak.py pack resources/ resources.vpak --key my-key
python3 tools/vne-packager/vpak.py list resources.vpak
python3 tools/vne-packager/vpak.py extract resources.vpak path/to/file --key my-key
```

暗号化：XOR + 256 バイト巡回キー（SHA256 派生）

---

## 要件

- Python 3.8+
- VoidNovelEngine プロジェクト

---

## ライセンス

MIT
