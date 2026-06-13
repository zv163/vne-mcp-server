<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-ゼロ-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="English"></a>
</p>

# VNE MCP Server

VoidNovelEngine 用 MCP サーバー。11 ツール、Python 標準ライブラリ、依存ゼロ。

---

## 目次

- [インストール](#インストール)
- [11 ツール](#11-ツール)
- [クライアント設定](#クライアント設定)
- [VPak](#vpak)

---

## インストール

`tools/` フォルダを VNE プロジェクトのルートに置くだけです：

```
VoidNovelEngine/
├── project.vne
├── application/
├── tools/                        ← ここに
│   ├── vne-mcp-server/
│   │   └── vne_mcp_server.py     ← MCP サーバー
│   └── vne-packager/
│       └── vpak.py               ← VPak パッケージャー
└── ...
```

```bash
# 方法1：クローンしてコピー
git clone https://github.com/zv163/vne-mcp-server.git
cp -r vne-mcp-server/tools/ あなたのVNEプロジェクト/

# 方法2：ZIP をダウンロードして tools/ をコピー
```

テスト：

```bash
python3 tools/vne-mcp-server/vne_mcp_server.py --info
python3 tools/vne-mcp-server/vne_mcp_server.py --list-tools
```

---

## 11 ツール

| # | ツール | 説明 | R/O |
|---|--------|------|:--:|
| 1 | `vne_project_info` | バージョン、アセット数、パス | ✓ |
| 2 | `vne_list_resources` | タイプ別リソース一覧 | ✓ |
| 3 | `vne_read_file` | ファイル読み取り | ✓ |
| 4 | `vne_list_directory` | ディレクトリ閲覧 | ✓ |
| 5 | `vne_search` | Lua スクリプト全文検索 | ✓ |
| 6 | `vne_get_resource` | リソース詳細（.meta 含む） | ✓ |
| 7 | `vne_lua_api` | エンジン Lua API リファレンス | ✓ |
| 8 | `vne_export_config` | エクスポート設定と VPak 状態 | ✓ |
| 9 | `vne_pack_resources` | 暗号化リソースパッケージを実行 | ✗ |
| 10 | `vne_read_vpak` | .vpak アーカイブ操作 | ✓ |
| 11 | `vne_console_log` | リアルタイムコンソールログ | ✓ |

---

## クライアント設定

### Claude Desktop

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/あなたのVNEプロジェクト/tools/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/あなたのVNEプロジェクト"
      ]
    }
  }
}
```

### Cursor / Windsurf

同じ形式です。

### Hermes Agent

```bash
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 /あなたのVNEプロジェクト/tools/vne-mcp-server/vne_mcp_server.py \
  --project-path /あなたのVNEプロジェクト "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh
```

### その他のクライアント

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/あなたのVNEプロジェクト/tools/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/あなたのVNEプロジェクト"
      ]
    }
  }
}
```

---

## VPak

`vne_pack_resources` と `vne_read_vpak` は `tools/vne-packager/vpak.py` に依存します。単体でも使用可能：

```bash
# パック
python3 tools/vne-packager/vpak.py pack resources/ resources.vpak --key my-key

# 一覧
python3 tools/vne-packager/vpak.py list resources.vpak

# 抽出
python3 tools/vne-packager/vpak.py extract resources.vpak ファイルパス --key my-key
```

暗号化：XOR + 256 バイト回転キー（SHA256 派生）

---

## 要件

- Python 3.8+
- VoidNovelEngine プロジェクト

---

## ライセンス

MIT
