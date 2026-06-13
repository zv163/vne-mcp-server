<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-零依赖-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.en.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="English"></a>
  <a href="README.ja.md"><img src="https://img.shields.io/badge/Lang-日本語-red?style=for-the-badge" alt="日本語"></a>
</p>

# VNE MCP Server

VoidNovelEngine 的 MCP 服务器。11 个工具，Python 标准库，零依赖。

---

## 目录

- [安装](#安装)
- [11 个工具](#11-个工具)
- [客户端配置](#客户端配置)
- [VPak 说明](#vpak-说明)

---

## 安装

把 `tools/` 文件夹放到 VNE 项目根目录即可：

```
VoidNovelEngine/
├── project.vne
├── application/
├── tools/                        ← 放这里
│   ├── vne-mcp-server/
│   │   └── vne_mcp_server.py     ← MCP 服务器
│   └── vne-packager/
│       └── vpak.py               ← VPak 打包器
└── ...
```

```bash
# 方法一：直接克隆
git clone https://github.com/zv163/vne-mcp-server.git
cp -r vne-mcp-server/tools/ 你的VNE项目路径/

# 方法二：下载 ZIP 解压后复制 tools/ 过去
```

测试：

```bash
python3 tools/vne-mcp-server/vne_mcp_server.py --info
python3 tools/vne-mcp-server/vne_mcp_server.py --list-tools
```

---

## 11 个工具

| # | 工具 | 功能 | 只读 |
|---|------|------|:--:|
| 1 | `vne_project_info` | 项目版本、资源统计、路径 | ✓ |
| 2 | `vne_list_resources` | 按类型列出资源 | ✓ |
| 3 | `vne_read_file` | 读取项目文件 | ✓ |
| 4 | `vne_list_directory` | 浏览目录 | ✓ |
| 5 | `vne_search` | 全文搜索 Lua 脚本 | ✓ |
| 6 | `vne_get_resource` | 资源详情（含 .meta） | ✓ |
| 7 | `vne_lua_api` | 引擎 Lua API 参考 | ✓ |
| 8 | `vne_export_config` | 导出配置和 VPak 状态 | ✓ |
| 9 | `vne_pack_resources` | 执行资源加密打包 | ✗ |
| 10 | `vne_read_vpak` | 列出/提取 .vpak 文件 | ✓ |
| 11 | `vne_console_log` | 实时编辑器控制台日志 | ✓ |

---

## 客户端配置

### Claude Desktop

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/你的VNE项目/tools/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/你的VNE项目"
      ]
    }
  }
}
```

### Cursor / Windsurf

同上。

### Hermes Agent

```bash
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 /你的VNE项目/tools/vne-mcp-server/vne_mcp_server.py \
  --project-path /你的VNE项目 "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh
```

### 其他客户端

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/你的VNE项目/tools/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/你的VNE项目"
      ]
    }
  }
}
```

---

## VPak 说明

`vne_pack_resources` 和 `vne_read_vpak` 依赖 `tools/vne-packager/vpak.py`。也可单独使用：

```bash
# 打包
python3 tools/vne-packager/vpak.py pack resources/ resources.vpak --key my-key

# 查看
python3 tools/vne-packager/vpak.py list resources.vpak

# 提取
python3 tools/vne-packager/vpak.py extract resources.vpak 文件路径 --key my-key
```

加密：XOR + 256 字节旋转密钥（SHA256 派生）

---

## 要求

- Python 3.8+
- VoidNovelEngine 项目

---

## License

MIT
