<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/Version-1.3.0-purple?style=for-the-badge" alt="v1.3.0">
  <img src="https://img.shields.io/badge/VNE-0.1.0+--dev.3-orange?style=for-the-badge" alt="VNE">
</p>

<p align="center">
  <a href="README.md">🇨🇳 中文</a> |
  <a href="README.en.md">🇬🇧 English</a> |
  <a href="README.ja.md">🇯🇵 日本語</a>
</p>

<h1 align="center">🔧 VNE ツールコレクション</h1>
<h3 align="center">VoidNovelEngine Tools Collection</h3>

<p align="center">
AI 駆動のビジュアルノベル開発ツールキット — MCP サーバー、カスタムノード、エンジンパッチ、シーンテンプレート、スキルライブラリ。
</p>

---

## 📑 ナビゲーション

- [🚀 MCP ツール](#-mcp-ツール-16個)
- [🧩 カスタムノード](#-カスタムノード)
- [🔩 エンジンパッチ](#-エンジンパッチ)
- [📚 スキルライブラリ](#-スキルライブラリ)
- [📦 インストール](#-インストール)
- [🔟 10の落とし穴](#-10の落とし穴)

---

## 🚀 MCP ツール (16個)

| ツール | 説明 |
|--------|------|
| `vne_project_info` | プロジェクト概要 |
| `vne_list_resources` | アセット一覧 |
| `vne_read_file` | ファイル読み取り |
| `vne_list_directory` | ディレクトリ一覧 |
| `vne_search` | ファイル検索 |
| `vne_get_resource` | リソース詳細 |
| `vne_lua_api` | Lua API リファレンス |
| `vne_export_config` | エクスポート設定 |
| `vne_pack_resources` | VPak パッケージ |
| `vne_read_vpak` | VPak 読み取り |
| `vne_console_log` | コンソールログ ★ |
| `vne_refresh_assets` | アセットキャッシュ更新 ★ |
| `vne_register_asset` | アセット登録 ★ |
| `vne_validate_flow` | .flow 検証 ★ |
| `vne_list_node_types` | ノードタイプ一覧 |
| `vne_reload_custom_nodes` | カスタムノードホットリロード ★★ |

> ★ = v1.2.0 追加  |  ★★ = v1.3.0 追加

---

## 📦 インストール

```bash
cd YourVNEProject/
git clone https://github.com/zv163/vne-mcp-server.git tools/vne-mcp-server
cp tools/vne-mcp-server/custom-nodes/dialog_line.lua application/node/custom/
# VNE を再起動
```

---

## 📄 ライセンス

MIT License
