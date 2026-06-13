<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/Version-1.2.0-purple?style=for-the-badge" alt="v1.2.0">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-零依赖-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.en.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="English"></a>
  <a href="README.ja.md"><img src="https://img.shields.io/badge/Lang-日本語-red?style=for-the-badge" alt="日本語"></a>
</p>

# VNE MCP Server

VoidNovelEngine 的 MCP 服务器。**15 个工具**，Python 标准库，零依赖。

让 AI 助手可以读取项目、搜索代码、管理资源、验证流程、查看控制台日志。

---

## 目录

- [安装](#安装)
- [15 个工具](#15-个工具)
- [v1.2.0 新功能](#v120-新功能)
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

## 15 个工具

| # | 工具 | 功能 | 只读 | 版本 |
|---|------|------|:--:|:--:|
| 1 | `vne_project_info` | 项目版本、资源统计、路径 | ✓ | 1.0 |
| 2 | `vne_list_resources` | 按类型列出资源 | ✓ | 1.0 |
| 3 | `vne_read_file` | 读取项目文件 | ✓ | 1.0 |
| 4 | `vne_list_directory` | 浏览目录 | ✓ | 1.0 |
| 5 | `vne_search` | 全文搜索 Lua 脚本 | ✓ | 1.0 |
| 6 | `vne_get_resource` | 资源详情（含 .meta） | ✓ | 1.0 |
| 7 | `vne_lua_api` | 引擎 Lua API 参考 | ✓ | 1.0 |
| 8 | `vne_export_config` | 导出配置和 VPak 状态 | ✓ | 1.0 |
| 9 | `vne_pack_resources` | 执行资源加密打包 | ✗ | 1.0 |
| 10 | `vne_read_vpak` | 列出/提取 .vpak 文件 | ✓ | 1.0 |
| 11 | `vne_console_log` | 实时编辑器控制台日志 | ✓ | 1.1 |
| 12 | `vne_refresh_assets` | 刷新资产缓存（无需重启引擎） | ✗ | **1.2** |
| 13 | `vne_register_asset` | 一键注册新资源（.meta + project.vne） | ✗ | **1.2** |
| 14 | `vne_validate_flow` | 验证 .flow 文件防崩溃 | ✓ | **1.2** |
| 15 | `vne_list_node_types` | 列出所有流程节点类型和引脚 | ✓ | **1.2** |

---

## v1.2.0 新功能

基于实际使用中遇到的问题，v1.2.0 新增了 4 个工具：

### 问题 1：创建文件后必须重启引擎

AI 通过外部工具创建 .vns/.flow 文件后，VNE 的 MCP 服务器缓存了旧的 asset registry，新文件不可见。

**解决**：`vne_refresh_assets` — 清除内部缓存，强制重新读取 project.vne。创建文件后调用一次即可。

### 问题 2：手动编辑 project.vne 易出错

注册新资源（.meta + asset_registry + open_flow_guid_list）需要手动编辑 JSON，容易格式错误。

**解决**：`vne_register_asset` — 传入文件路径和类型，自动创建 .meta、生成 GUID、写入 project.vne。一步完成，不会出错。

### 问题 3：手动生成 .flow 容易崩溃

手工拼接 .flow JSON 时，引脚 key 写错（如 choice 用 `route_1` 而非 `choice_1`）、merge_flow 缺少 key 等，会导致 VNE 编辑器双击崩溃。

**解决**：
- `vne_validate_flow` — 检查 JSON 结构、引脚 key 正确性、链接完整性。**生成 .flow 后、打开前必须调用。**
- `vne_list_node_types` — 列出 70+ 节点类型的完整引脚 schema，生成流程前查看，避免写错 key。

### 推荐工作流

```
1. vne_list_node_types     → 了解可用的节点和引脚名
2. 生成 .flow 文件         → 用 Python 脚本或其他方式
3. vne_validate_flow       → 验证无错误
4. vne_register_asset      → 自动注册到项目
5. vne_refresh_assets      → 刷新缓存
6. 在 VNE 编辑器中打开     → 安全无忧
```

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
