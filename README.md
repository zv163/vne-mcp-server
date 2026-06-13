# VNE MCP Server · 11工具 · 零依赖

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-2024--11--05-green)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

> A Model Context Protocol (MCP) server for VoidNovelEngine projects.
> AI 助手与 VoidNovelEngine 项目交互的 MCP 服务器。
> VoidNovelEngine プロジェクトを AI アシスタントが操作するための MCP サーバー。

---

## 📋 Features · 功能一覧 · 機能一覧

**11 Tools** — read, search, pack, debug — everything an AI needs to understand and work with a VNE project.

| # | Tool | What it does | 做什么 | 機能 |
|---|------|-------------|--------|------|
| 1 | `vne_project_info` | Project overview: version, asset counts, paths | 项目概况：版本、资源统计 | プロジェクト概要 |
| 2 | `vne_list_resources` | List resources by type (texture, audio, flow…) | 按类型列出资源 | リソース一覧 |
| 3 | `vne_read_file` | Read any project file | 读取项目文件 | ファイル読み取り |
| 4 | `vne_list_directory` | Browse directory contents | 浏览目录结构 | ディレクトリ一覧 |
| 5 | `vne_search` | Full-text search across Lua scripts | 全文搜索 Lua 脚本 | テキスト検索 |
| 6 | `vne_get_resource` | Resource detail by GUID (with .meta) | 资源详情（含 .meta） | リソース詳細 |
| 7 | `vne_lua_api` | Engine Lua API reference | 引擎 Lua API 参考 | エンジン API リファレンス |
| 8 | `vne_export_config` | Export settings & VPak status | 导出配置查看 | エクスポート設定 |
| 9 | `vne_pack_resources` | Run VPak resource packaging | 执行资源打包 | リソースパック |
| 10 | `vne_read_vpak` | List / extract from .vpak archives | 读取 .vpak 归档 | VPak アーカイブ操作 |
| 11 | `vne_console_log` | Real-time editor console log | 实时控制台日志 | リアルタイムコンソールログ |

---

## 🚀 Quick Start · 快速开始 · クイックスタート

### Requirements · 环境要求

- **Python 3.8+** — no external dependencies, stdlib only
- A VoidNovelEngine project with `project.vne`

```bash
# Test: show project info
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine --info

# Test: list all textures
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine --resources texture

# Test: list all available tools
python vne_mcp_server.py --list-tools
```

### Stdio Mode (default, for MCP clients)

```bash
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine
```

### TCP/HTTP Mode (for Lua host integration)

```bash
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine --port 8765
```

Endpoints:
- SSE: `http://127.0.0.1:8765/sse`
- Message: `http://127.0.0.1:8765/message`
- Health: `http://127.0.0.1:8765/health`

---

## 🔧 Client Configuration · 客户端配置

### Claude Desktop

Edit `claude_desktop_config.json`:

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

Same JSON format, add to your MCP configuration file.

### Hermes Agent

```bash
# Create a wrapper script
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 /path/to/vne-mcp-server/vne_mcp_server.py \
  --project-path /path/to/VoidNovelEngine "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh

# Register with Hermes
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh
```

### Generic MCP Client

Any client that supports MCP stdio transport:

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

## 📦 Transport Modes · 传输模式

| Mode | Trigger | Use Case |
|------|---------|----------|
| **Stdio** (default) | No `--port` or `--stdio` | Claude Desktop, Cursor, any MCP client |
| **TCP/HTTP** | `--port 8765` | Embedded in VNE editor via Lua host |

### How TCP mode works with VNE editor

The VNE editor includes a Lua MCP host (`mcp_host.lua`) that:

1. Auto-discovers Python on Windows
2. Launches `vne_mcp_server.py --port 8765` as a child process
3. Watches stdout for `VNE_MCP_READY host=127.0.0.1 port=8765`
4. Opens SSE connection to receive real-time log events
5. Bridges `LogManager.log()` output to `save/diagnostics/mcp_console.jsonl` — enabling **`vne_console_log`** tool for AI to read editor console in near-real-time

---

## 🔐 VPak Integration

Two tools interact with VPak encrypted archives:

- **`vne_pack_resources`** — spawns `vpak.py pack` as subprocess (XOR encryption, optional zlib compression)
- **`vne_read_vpak`** — directly imports `vpak.py` module to list/extract files

Both use `vpak.py` (VPak packager) — included in this repo for standalone use:

```bash
# Pack resources
python vpak.py pack application/resources application/resources.vpak --key my-secret-key

# List archive contents
python vpak.py list application/resources.vpak

# Extract a file
python vpak.py extract application/resources.vpak texture/icon.png --key my-secret-key
```

---

## 📁 Files · 文件结构

```
vne-mcp-server/
├── vne_mcp_server.py   # Main MCP server (1118 lines, 11 tools)
├── vpak.py             # VPak packager (316 lines, XOR + zlib)
└── README.md           # You are here
```

---

## 🛠 Architecture · 架构

```
                    ┌─────────────────────┐
                    │   AI Assistant       │
                    │ (Claude / GPT / etc) │
                    └──────┬──────────────┘
                           │ MCP (stdio / HTTP SSE)
                    ┌──────▼──────────────┐
                    │  vne_mcp_server.py   │
                    │  ┌────────────────┐  │
                    │  │  MCP Protocol   │  │
                    │  │  (JSON-RPC 2.0) │  │
                    │  ├────────────────┤  │
                    │  │  VNEProject     │  │
                    │  │  - project.vne  │  │
                    │  │  - asset index  │  │
                    │  │  - file reader  │  │
                    │  │  - searcher     │  │
                    │  ├────────────────┤  │
                    │  │  VPak module    │  │
                    │  │  - vpak.py      │  │
                    │  ├────────────────┤  │
                    │  │  Console Bridge │  │
                    │  │  - jsonl reader │  │
                    │  └────────────────┘  │
                    └──────┬──────────────┘
                           │ file read / subprocess
                    ┌──────▼──────────────┐
                    │  VNE Project         │
                    │  ├── project.vne     │
                    │  ├── application/    │
                    │  │   ├── resources/  │
                    │  │   ├── framework/  │
                    │  │   └── scene/      │
                    │  └── save/           │
                    │      └── diagnostics/│
                    └─────────────────────┘
```

---

## 🌐 中文说明

### 什么是 VNE MCP Server？

这是一个 MCP（模型上下文协议）服务器，让 AI 助手可以直接与 VoidNovelEngine（一款基于 Lua 的可视化小说引擎）项目交互。

### 11 个工具

1. **vne_project_info** — 查看项目版本、资源统计、路径信息
2. **vne_list_resources** — 按类型（纹理、音频、流程脚本等）列出所有资源
3. **vne_read_file** — 读取项目中的任意文件
4. **vne_list_directory** — 浏览目录结构
5. **vne_search** — 在 Lua 脚本中全文搜索
6. **vne_get_resource** — 通过 GUID 获取资源详情（含 .meta 元数据）
7. **vne_lua_api** — 获取引擎 Lua API 参考文档
8. **vne_export_config** — 查看导出配置和 VPak 状态
9. **vne_pack_resources** — 执行 VPak 资源加密打包
10. **vne_read_vpak** — 列出或提取 .vpak 归档中的文件
11. **vne_console_log** — 实时读取 VNE 编辑器控制台日志

### 安装和使用

```bash
# 1. 确保 Python 3.8+
python --version

# 2. 克隆仓库
git clone https://github.com/zv163/vne-mcp-server.git
cd vne-mcp-server

# 3. 测试
python vne_mcp_server.py --project-path /你的/VoidNovelEngine/路径 --info

# 4. 配置到 AI 客户端（见上方 Client Configuration）
```

### 零依赖

整个服务器使用 Python 标准库编写，不需要安装任何第三方包。

---

## 🇯🇵 日本語説明

### VNE MCP Server とは？

Model Context Protocol (MCP) に対応したサーバーで、AI アシスタントが VoidNovelEngine（Lua ベースのビジュアルノベルエンジン）プロジェクトを直接操作できるようにします。

### 11 のツール

1. **vne_project_info** — プロジェクトのバージョン、アセット数、パスを表示
2. **vne_list_resources** — タイプ別（テクスチャ、音声、フロー等）にリソースを一覧
3. **vne_read_file** — プロジェクト内の任意のファイルを読み取り
4. **vne_list_directory** — ディレクトリ構造を閲覧
5. **vne_search** — Lua スクリプト内を全文検索
6. **vne_get_resource** — GUID でリソース詳細（.meta 含む）を取得
7. **vne_lua_api** — エンジンの Lua API リファレンスを取得
8. **vne_export_config** — エクスポート設定と VPak 状態を確認
9. **vne_pack_resources** — VPak リソース暗号化パッケージを実行
10. **vne_read_vpak** — .vpak アーカイブの一覧表示・ファイル抽出
11. **vne_console_log** — VNE エディタのコンソールログをリアルタイム取得

### インストールと使用方法

```bash
# 1. Python 3.8+ を確認
python --version

# 2. リポジトリをクローン
git clone https://github.com/zv163/vne-mcp-server.git
cd vne-mcp-server

# 3. テスト実行
python vne_mcp_server.py --project-path /VoidNovelEngine/の/パス --info

# 4. AI クライアントに設定（上記「Client Configuration」参照）
```

### ゼロ依存

サーバー全体が Python 標準ライブラリのみで実装されており、サードパーティパッケージは一切不要です。

---

## 📜 License

MIT — see [LICENSE](LICENSE) file.

---

## 🔗 Links

- [VoidNovelEngine](https://github.com/VoidmatrixHeathcliff/VoidNovelEngine) — The visual novel engine
- [Model Context Protocol](https://modelcontextprotocol.io) — MCP specification
