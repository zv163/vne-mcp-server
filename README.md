<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/Version-1.3.0-purple?style=for-the-badge" alt="v1.3.0">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/VNE-0.1.0+--dev.3-orange?style=for-the-badge" alt="VNE">
</p>

<p align="center">
  <a href="README.md">🇨🇳 中文</a> |
  <a href="README.en.md">🇬🇧 English</a> |
  <a href="README.ja.md">🇯🇵 日本語</a>
</p>

<h1 align="center">🔧 VNE 工具合集</h1>
<h3 align="center">VoidNovelEngine Tools Collection — v1.3.0</h3>

<p align="center">
MCP 服务端 · 自定义节点 · 引擎补丁 · 场景生成器 · VPak 打包器
<br>
一套覆盖视觉小说开发全流程的 AI 辅助工具链
</p>

---

## 📑 导航

| 章节 | 说明 |
|------|------|
| [✨ 功能介绍](#-功能介绍) | 工具集能力总览 |
| [📦 安装指南](#-安装指南) | 三类安装教程入口 |
| [🔧 安装一：工具安装](#-安装一工具安装) | 部署到 VNE 项目 |
| [🔌 安装二：MCP 客户端配置](#-安装二mcp-客户端配置) | Cursor / Trae / Claude / Hermes |
| [📚 安装三：技能安装](#-安装三技能安装) | Hermes Agent 技能加载 |
| [🏗️ 仓库结构](#-仓库结构) | 目录说明 |

---

## ✨ 功能介绍

本工具集为 VoidNovelEngine 视觉小说引擎提供完整的 AI 辅助开发能力：

### 🔌 MCP 服务端 — 16 个 AI 工具

让 AI 助手能直接操作 VNE 项目：

- **项目信息**：读取项目配置、Lua API 参考、导出设置
- **资源管理**：列出/搜索/注册资产，刷新缓存
- **流图操作**：校验 .flow 文件（防崩溃）、查看节点类型
- **VPak 打包**：加密打包资源、读取 .vpak 内容
- **调试开发**：实时控制台日志、自定义节点热重载

支持 **Cursor**、**Trae**、**Claude Desktop**、**Hermes Agent** 等所有 MCP 兼容客户端。

### 🧩 自定义节点

`dialog_line` — 将「隐藏上句 + 播放音频 + 显示对话」合并为一个节点，传统 4 节点 → 1 节点。

### 🔩 引擎补丁

mcp_host.lua 热重载补丁 — 修改自定义节点后无需重启 VNE，AI 工具一键触发。

### 📚 技能库

4 个 Hermes Agent 技能，自动注入 VNE 领域知识：
- `void-novel-engine` — 引擎架构、API、十大陷阱
- `vne-flow-patterns` — 节点连接模式与布局规范
- `vne-scene-recipes` — 校园恋爱场景模板
- `vne-custom-extensions` — 自定义节点开发指南

---

## 内容概览

| 组件 | 说明 |
|------|------|
| `tools/vne-mcp-server/` | MCP 服务端，16 个 AI 工具 |
| `tools/vne-packager/` | VPak 资源打包器 |
| `custom-nodes/` | 自定义节点（dialog_line 等） |
| `engine-patches/` | 引擎补丁（热重载等） |
| `skills/` | Hermes Agent 技能库 |
| `examples/` | 测试流示例 |

---

## 📦 安装指南

本工具集包含三类组件，安装方式各不相同：

| 教程 | 适用对象 | 跳转 |
|------|---------|------|
| 🔧 **工具安装** | 所有用户 — 将工具部署到 VNE 项目 | [→](#-安装一工具安装) |
| 🔌 **MCP 客户端配置** | AI 助手用户 — 连接 Cursor / Trae / Claude / Hermes | [→](#-安装二mcp-客户端配置) |
| 📚 **技能安装** | Hermes Agent 用户 — 加载 VNE 技能 | [→](#-安装三技能安装) |

---

## 🔧 安装一：工具安装

将本仓库的工具部署到 VNE 项目中。

### 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| VNE 编辑器 | 0.1.0-dev.3+ | 项目能正常打开运行 |
| Python | 3.8+ | VNE 自动从 PATH 和常见目录检测 |
| Git | 任意 | 用于克隆仓库 |
| 操作系统 | Windows | VNE 仅支持 Windows |

MCP 服务端**零 pip 依赖**，仅使用 Python 标准库。

### 步骤

```bash
# 1. 进入 VNE 项目根目录
cd D:\YourVNEProject\

# 2. 克隆工具集
git clone https://github.com/zv163/vne-mcp-server.git tools/vne-mcp-server

# 3. 复制自定义节点（可选）
cp tools/vne-mcp-server/custom-nodes/dialog_line.lua application/node/custom/

# 4. 重启 VNE 编辑器
```

### 验证

重启后控制台出现即成功：

```
MCP 服务已就绪 http://127.0.0.1:8765
```

如果未出现，检查 Python 是否可被发现（`python --version` 能正常输出即可）。

### 启用热重载（可选）

编辑 `application/framework/mcp_host.lua`，按 `engine-patches/mcp_host_hotreload.md` 添加 22 行代码。改自定义节点后无需重启 VNE。

### 卸载

```bash
rm -rf tools/vne-mcp-server/
rm application/node/custom/dialog_line.lua
```

---

## 🔌 安装二：MCP 客户端配置

VNE MCP 服务端在 `127.0.0.1:8765` 提供 HTTP/SSE 传输。以下为各客户端配置方法。

### 通用信息

```
传输协议: SSE (HTTP)
服务地址: http://127.0.0.1:8765
SSE 端点: http://127.0.0.1:8765/sse
消息端点: http://127.0.0.1:8765/message
```

> VNE 启动后 MCP 服务端自动运行，无需手动启动。

---

### Cursor

编辑 Cursor 的 MCP 配置文件（`~/.cursor/mcp.json`）：

```json
{
  "mcpServers": {
    "vne": {
      "transport": "sse",
      "url": "http://127.0.0.1:8765/sse"
    }
  }
}
```

重启 Cursor，在 AI 面板中即可使用 `vne_*` 工具。

---

### Trae

编辑 Trae MCP 配置：

```json
{
  "mcpServers": {
    "vne": {
      "type": "sse",
      "url": "http://127.0.0.1:8765/sse"
    }
  }
}
```

---

### Claude Desktop

编辑 Claude Desktop 配置（`%APPDATA%\Claude\claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "vne": {
      "command": "npx",
      "args": [
        "-y", "@anthropic/mcp-client-sse",
        "http://127.0.0.1:8765/sse"
      ]
    }
  }
}
```

或使用 stdio 代理：

```json
{
  "mcpServers": {
    "vne": {
      "command": "python",
      "args": [
        "tools/vne-mcp-server/tools/vne-mcp-server/vne_mcp_server.py",
        "--project-path", ".",
        "--stdio"
      ]
    }
  }
}
```

---

### Hermes Agent

Hermes 通过其 MCP 插件原生支持 SSE 传输。在 `config.yaml` 中配置：

```yaml
mcp:
  servers:
    - name: vne
      transport: sse
      url: http://127.0.0.1:8765/sse
```

或在终端中：

```bash
hermes mcp add vne --transport sse --url http://127.0.0.1:8765/sse
```

重启 Hermes 后执行 `vne_project_info` 验证连接。

---

### 验证 MCP 连接

在 AI 助手中执行：

```
vne_project_info
```

返回项目信息（标题、资产数量、路径等）即连接成功。

---

## 📚 安装三：技能安装

技能（Skills）是 Hermes Agent 的领域知识模块。VNE 工具合集包含 4 个技能。

### 自动安装

```bash
# 克隆仓库后，技能已在 skills/ 目录
# Hermes 自动发现 ~/.hermes/skills/ 下的技能

# 创建软链接
mkdir -p ~/.hermes/skills/software-development
ln -s "$(pwd)/tools/vne-mcp-server/skills/void-novel-engine" \
      ~/.hermes/skills/software-development/void-novel-engine
ln -s "$(pwd)/tools/vne-mcp-server/skills/vne-flow-patterns" \
      ~/.hermes/skills/software-development/vne-flow-patterns
ln -s "$(pwd)/tools/vne-mcp-server/skills/vne-scene-recipes" \
      ~/.hermes/skills/software-development/vne-scene-recipes
ln -s "$(pwd)/tools/vne-mcp-server/skills/vne-custom-extensions" \
      ~/.hermes/skills/software-development/vne-custom-extensions
```

### 技能列表

| 技能名 | 用途 |
|--------|------|
| `void-novel-engine` | VNE 引擎全面指南：架构、API、VPak、.flow、十大陷阱 |
| `vne-flow-patterns` | 节点连接模式：对话框、分支、前景图、楼梯布局 |
| `vne-scene-recipes` | 场景模板：教室、樱花树、天台 |
| `vne-custom-extensions` | 自定义节点开发：`make_definition`、`try_check_input` |

安装后，AI 在处理 VNE 相关任务时会自动加载对应技能。

---

## 🏗️ 仓库结构

```
vne-mcp-server/
├── tools/
│   ├── vne-mcp-server/vne_mcp_server.py   ← MCP 服务端 (16 工具)
│   └── vne-packager/vpak.py               ← VPak 打包器
├── custom-nodes/dialog_line.lua           ← 合并对话节点
├── engine-patches/mcp_host_hotreload.md   ← 热重载补丁
├── skills/                                ← Hermes Agent 技能
├── examples/_dialog_line_test.flow        ← 测试流
├── README.md / README.en.md / README.ja.md
└── LICENSE (MIT)
```

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)

---

<p align="center">
  <sub>Made with ❤️ for VNE visual novel development</sub>
</p>
