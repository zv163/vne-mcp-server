<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-零依赖-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.en.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="English"></a>
  <a href="README.ja.md"><img src="https://img.shields.io/badge/Lang-日本語-red?style=for-the-badge" alt="日本語"></a>
</p>

# VNE MCP Server

**VoidNovelEngine 的 MCP（模型上下文协议）服务器。** 让 AI 助手可以读取、搜索、打包、调试 VNE 项目。11 个工具，纯 Python 标准库，零外部依赖。

---

## 目录

- [📦 安装与文件放置](#-安装与文件放置)
- [🛠 11 个工具](#-11-个工具)
- [🚀 快速开始](#-快速开始)
- [🔧 客户端配置](#-客户端配置)
  - [Claude Desktop](#claude-desktop)
  - [Cursor / Windsurf](#cursor--windsurf)
  - [Hermes Agent](#hermes-agent)
  - [通用 MCP 客户端](#通用-mcp-客户端)
- [🔗 TCP 模式与编辑器集成](#-tcp-模式与-vne-编辑器集成)
- [🔐 VPak 集成](#-vpak-集成)
- [📁 文件结构](#-文件结构)
- [📋 环境要求](#-环境要求)
- [🔗 相关链接](#-相关链接)

---

## 📦 安装与文件放置

### 文件说明

本仓库包含 **两个 Python 文件**，缺一不可：

| 文件 | 作用 | 是否必需 |
|------|------|:---:|
| `vne_mcp_server.py` | MCP 服务器主程序（11 个工具） | ✓ 必需 |
| `vpak.py` | VPak 打包/解包模块 | ✓ 必需 |

`vne_mcp_server.py` 的 `vne_pack_resources` 和 `vne_read_vpak` 工具需要调用 `vpak.py`，因此 **两个文件必须放在同一目录下**。

### 安装步骤

```bash
# 1. 克隆仓库到本地（推荐放在用户目录下）
git clone https://github.com/zv163/vne-mcp-server.git ~/vne-mcp-server

# 2. 确认文件都在
ls ~/vne-mcp-server/
# 输出: vne_mcp_server.py  vpak.py  README.md  LICENSE

# 3. 确认 Python 版本（3.8+）
python3 --version

# 4. 测试是否正常工作
python3 ~/vne-mcp-server/vne_mcp_server.py --list-tools
```

> **路径建议：** 放在 `~/vne-mcp-server/` 或任意固定路径即可。不要放在 VNE 项目内部——这是一个独立工具，可以同时服务于多个 VNE 项目。

### 目录结构总览

```
~/vne-mcp-server/              ← 推荐安装位置（用户目录）
├── vne_mcp_server.py          ← MCP 服务器主程序
├── vpak.py                    ← VPak 打包模块（必须在同目录）
├── README.md / .en.md / .ja.md
└── LICENSE

/path/to/VoidNovelEngine/      ← 你的 VNE 项目（任意位置）
├── project.vne
├── application/
│   ├── resources/
│   ├── framework/
│   └── scene/
└── save/diagnostics/
```

---

## 🛠 11 个工具

| # | 工具名 | 功能 | 只读 |
|---|--------|------|:----:|
| 1 | `vne_project_info` | 项目概况 — 版本号、资源统计、路径信息 | ✓ |
| 2 | `vne_list_resources` | 按类型列出资源（纹理、音频、流程脚本等） | ✓ |
| 3 | `vne_read_file` | 读取项目中任意文件内容 | ✓ |
| 4 | `vne_list_directory` | 浏览项目目录结构 | ✓ |
| 5 | `vne_search` | 在 Lua 脚本中全文搜索（不区分大小写） | ✓ |
| 6 | `vne_get_resource` | 通过 GUID 获取资源详情（含 .meta 元数据） | ✓ |
| 7 | `vne_lua_api` | 引擎 Lua API 参考 — 模块、类、资源类型映射 | ✓ |
| 8 | `vne_export_config` | 查看导出配置 — 标题、入口流程、VPak 状态 | ✓ |
| 9 | `vne_pack_resources` | 执行 VPak 资源加密打包（XOR 加密 + zlib 压缩） | ✗ |
| 10 | `vne_read_vpak` | 列出 / 提取 .vpak 归档文件 | ✓ |
| 11 | `vne_console_log` | 实时读取 VNE 编辑器控制台日志 | ✓ |

---

## 🚀 快速开始

```bash
# 查看项目信息
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine --info

# 列出所有纹理资源
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine --resources texture

# 查看所有可用工具
python3 ~/vne-mcp-server/vne_mcp_server.py --list-tools
```

### Stdio 模式（默认，用于 MCP 客户端）

```bash
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine
```

### TCP/HTTP 模式（嵌入 VNE 编辑器）

```bash
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine --port 8765
```

| 端点 | 用途 |
|------|------|
| `http://127.0.0.1:8765/sse` | SSE 推送通道 |
| `http://127.0.0.1:8765/message` | 消息接收 |
| `http://127.0.0.1:8765/health` | 健康检查 |

---

## 🔧 客户端配置

> **注意：** 以下示例中的 `/path/to/vne-mcp-server/` 需要替换为你的实际安装路径（如 `~/vne-mcp-server`）。

### Claude Desktop

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/home/你的用户名/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/path/to/VoidNovelEngine"
      ]
    }
  }
}
```

### Cursor / Windsurf

同上 JSON 格式，添加到 MCP 配置文件即可。

### Hermes Agent

```bash
# 1. 创建包装脚本
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 ~/vne-mcp-server/vne_mcp_server.py \
  --project-path /mnt/d/A-Game/VoidNovelEngine "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh

# 2. 注册到 Hermes
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh

# 3. 验证
hermes mcp list | grep vne
```

> **注意：** 如果 `hermes mcp add` 报错说 `--project-path` 无法识别，就用包装脚本的方式（如上），不要让 hermes 直接传 `--project-path` 参数。

### 通用 MCP 客户端

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

## 🔗 TCP 模式与 VNE 编辑器集成

VNE 编辑器内置 Lua MCP 宿主 (`mcp_host.lua`)，启动时自动：

1. 发现 Python 路径
2. 启动 `vne_mcp_server.py --port 8765` 子进程
3. 等待 `VNE_MCP_READY` 信号
4. 建立 SSE 连接
5. 桥接 `LogManager.log()` → `save/diagnostics/mcp_console.jsonl`

这使得 **`vne_console_log`** 工具可以让 AI 近乎实时地读取编辑器控制台。

```
┌─────────────────────────┐
│     AI 助手              │
│  (Claude / GPT / Cursor) │
└─────┬───────────────────┘
      │ MCP (stdio / HTTP SSE)
┌─────▼───────────────────┐
│   vne_mcp_server.py      │
│  ┌─────────────────────┐ │
│  │  MCP 协议层          │ │
│  │  (JSON-RPC 2.0)     │ │
│  ├─────────────────────┤ │
│  │  VNEProject 内核     │ │
│  │  · project.vne 解析  │ │
│  │  · 资源索引          │ │
│  │  · 文件读写          │ │
│  │  · 全文搜索          │ │
│  ├─────────────────────┤ │
│  │  VPak 模块           │ │
│  │  · vpak.py 子进程    │ │
│  ├─────────────────────┤ │
│  │  控制台桥接          │ │
│  │  · jsonl 读取        │ │
│  └─────────────────────┘ │
└─────┬───────────────────┘
      │ 文件读取 / 子进程
┌─────▼───────────────────┐
│  VNE 项目                │
│  ├── project.vne        │
│  ├── application/       │
│  │   ├── resources/     │
│  │   ├── framework/     │
│  │   └── scene/         │
│  └── save/diagnostics/  │
└─────────────────────────┘
```

---

## 🔐 VPak 集成

- **`vne_pack_resources`** — 调用 `vpak.py pack` 子进程（XOR 加密，可选 zlib）
- **`vne_read_vpak`** — 导入 `vpak.py` 模块列出 / 提取文件

`vpak.py` 也可独立使用：

```bash
# 打包
python3 ~/vne-mcp-server/vpak.py pack  resources/  resources.vpak --key my-key

# 列出
python3 ~/vne-mcp-server/vpak.py list  resources.vpak

# 提取
python3 ~/vne-mcp-server/vpak.py extract  resources.vpak  texture/icon.png --key my-key
```

### VPak 格式

| 段 | 大小 | 说明 |
|----|------|------|
| Magic | 4 字节 | `VPAK` |
| Version | 4 字节 | uint32 LE |
| Flags | 4 字节 | bit0=加密, bit1=压缩 |
| File Count | 4 字节 | uint32 LE |
| File Table | N×32 字节 | 路径哈希 + 偏移 + 大小 |
| Data | N 字节 | 文件数据 |

加密：XOR 密码，256 字节旋转密钥（SHA256 + 确定性置乱派生）

---

## 📁 文件结构

```
vne-mcp-server/
├── vne_mcp_server.py   # 主服务器 (1118 行，11 个工具)
├── vpak.py             # VPak 打包器 (316 行，XOR + zlib)
├── README.md           # 本文件（中文）
├── README.en.md        # 英文版
├── README.ja.md        # 日文版
└── LICENSE             # MIT
```

---

## 📋 环境要求

- **Python 3.8+** — 纯标准库，无需 pip install
- VoidNovelEngine 项目（含 `project.vne`）

---

## 🔗 相关链接

- [VoidNovelEngine](https://github.com/VoidmatrixHeathcliff/VoidNovelEngine) — 可视化小说引擎
- [Model Context Protocol](https://modelcontextprotocol.io) — MCP 协议规范
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — 自进化 AI 代理

---

## License

MIT — 详见 [LICENSE](LICENSE)
