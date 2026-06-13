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
<h3 align="center">VoidNovelEngine Tools Collection</h3>

<p align="center">
AI 驱动的视觉小说开发工具集 — MCP 服务端、自定义节点、引擎补丁、场景模板、技能库。
<br>
让 AI 助手能读写校验 .flow 文件、热重载自定义节点、一键生成场景。
</p>

---

## 📑 导航

| 分类 | 内容 |
|------|------|
| [🚀 MCP 工具](#-mcp-工具-16-个) | 16 个 AI 可调用工具 |
| [🧩 自定义节点](#-自定义节点) | `dialog_line` 合并对话节点 |
| [🔩 引擎补丁](#-引擎补丁) | mcp_host.lua 热重载补丁 |
| [📚 技能库](#-技能库) | 4 个 AI 技能 |
| [📐 场景示例](#-场景示例) | 校园恋爱 .flow 示例 |
| [📦 安装](#-安装) | 安装指南 |
| [🔟 十大陷阱](#-十大陷阱) | VNE 开发常见陷阱 |

---

## 🚀 MCP 工具 (16 个)

提供 16 个 MCP (Model Context Protocol) 工具，AI 助手可通过这些工具直接操作 VNE 项目。

### 项目信息

| 工具 | 说明 |
|------|------|
| `vne_project_info` | 获取项目概览（版本、资产统计、路径） |
| `vne_lua_api` | 获取 VNE Lua API 参考文档 |
| `vne_export_config` | 获取导出配置（入口流程、VPak 状态） |

### 资源管理

| 工具 | 说明 |
|------|------|
| `vne_list_resources` | 列出所有资产（可按类型过滤：flow, texture, audio...） |
| `vne_list_directory` | 列出目录内容 |
| `vne_get_resource` | 获取指定 GUID 的资源详情 |
| `vne_refresh_assets` | 刷新资产缓存（外部创建文件后调用）★ |
| `vne_register_asset` | 原子化注册资产（创建 .meta + 写 project.vne）★ |

### 文件操作

| 工具 | 说明 |
|------|------|
| `vne_read_file` | 读取项目内文件 |
| `vne_search` | 搜索项目文件内容 |

### 流图（Flow）操作

| 工具 | 说明 |
|------|------|
| `vne_validate_flow` | 校验 .flow 文件（防崩溃：检查 pin key、psv、节点上限）★ |
| `vne_list_node_types` | 列出所有可用节点类型及引脚 schema |

### VPak 打包

| 工具 | 说明 |
|------|------|
| `vne_pack_resources` | 打包资源为加密 .vpak |
| `vne_read_vpak` | 列出/提取 .vpak 内容 |

### 调试 & 开发

| 工具 | 说明 |
|------|------|
| `vne_console_log` | 实时读取 VNE 编辑器控制台日志 ★ |
| `vne_reload_custom_nodes` | 热重载自定义节点（无需重启 VNE）★ |

> ★ = v1.2.0+ 新增  |  ★★ = v1.3.0 新增

---

## 🧩 自定义节点

### `dialog_line` — 合并对话行

**文件**: `custom-nodes/dialog_line.lua` (101 行)  
**类型 ID**: `dialog_line`  
**类别**: 演出控制

一个节点完成：**隐藏上一句 + 播放音频(可选) + 显示当前对话**。

```
传统方式 (4 节点):                 dialog_line (1 节点):
show_dialog_box ──→ hide ──→       ┌─ prev_dialog (可选，链式)
                    play_audio ──→  ├─ role_text
                    show_dialog_box ├─ dialogue_text
                                    ├─ audio (可选，无则跳过)
                                    └─ volume (默认 0.8)
```

**链式连接**：`nodeA.dialog_box` → `nodeB.prev_dialog`

**效果**：4 节点 → 1 节点。10 句对话从 40 节点降到 10 节点。

---

## 🔩 引擎补丁

### Hot-Reload 补丁

**文件**: `engine-patches/mcp_host_hotreload.md`  
**目标**: `application/framework/mcp_host.lua`

在 `mcp_host.lua` 的 update 循环中加入 flag 文件检测，配合 `vne_reload_custom_nodes` 工具实现热重载。

```
MCP 工具                         VNE 引擎
  │                                │
  ├─ 写 flag 文件 ──────────────→ │
  │                                ├─ 每帧检测 flag
  │                                ├─ 找到 → definition_loader.load()
  │                                ├─ 重载所有节点定义
  │   ←────────────── 写 result ──┤
  │                                │
  ├─ 读 result → 返回成功/失败
```

**注意**：重载后需关闭并重新打开使用自定义节点的 .flow 文件。

---

## 📚 技能库

4 个 AI 技能，供 Hermes Agent 加载使用。

### `void-novel-engine`
VNE 引擎全面指南：项目结构、资源类型映射、MCP 工具 API、VPak 规范、.flow 格式。

### `vne-flow-patterns`
.flow 节点连接模式：对话框生命周期、分支/循环、前景图片、楼梯布局、生成模板。

### `vne-scene-recipes`
即用场景模板：教室表白、樱花树告别、天台谈心等校园恋爱场景。

### `vne-custom-extensions`
自定义节点开发指南：`make_definition` API、引脚定义、`try_check_input` 用法。

---

## 📐 场景示例

`examples/_dialog_line_test.flow` — 6 节点测试流，演示 `dialog_line` 链式用法：

```
entry → set_style → dialog_line(张晨) → dialog_line(小美+BGM) → dialog_line(林雪) → 菜单
```

---

## 📦 安装

```bash
# 1. Clone 到 VNE 项目目录
cd YourVNEProject/
git clone https://github.com/zv163/vne-mcp-server.git tools/vne-mcp-server

# 2. 复制自定义节点到项目
cp tools/vne-mcp-server/custom-nodes/dialog_line.lua application/node/custom/

# 3. (可选) 应用引擎补丁 — 见 engine-patches/mcp_host_hotreload.md

# 4. 重启 VNE 编辑器，MCP 工具自动可用
```

---

## 🔟 十大陷阱

在开发校园恋爱项目中发现并记录的 VNE 引擎陷阱：

| # | 陷阱 | 正确做法 |
|---|------|---------|
| 1 | `show_choice_button` 输出 key 是 `route_1` | 应该是 `choice_1`~`choice_5` |
| 2 | `add_foreground` 缺 `shader` pin | pin_schema_version 必须为 2，需含 shader |
| 3 | `merge_flow` 输入 pin 缺 key | 避免使用此节点 |
| 4 | 单 .flow 超过 80 节点 | 编辑器卡死，拆分为多场景 |
| 5 | `show_dialog_box` 不自动替换 | 需显式 `hide_dialog_box` 链接 |
| 6 | 隐藏/显示对话框无链接 | 需 `hide(fade=0.05)` + `show` 双链接 |
| 7 | 同场景换背景 | 换背景 = `switch_scene`，每场景 < 60 节点 |
| 8 | 分支引脚 key 不匹配 | `show_choice_button` → `choice_1`，不是 `branch_1` |
| 9 | link 的 pin_id 是 string | pin_id 必须是 int |
| 10 | 启动崩溃 | 删除 project.vne 中无效的 `current_graph_flow_guid` |

---

## 🏗️ 仓库结构

```
vne-mcp-server/
├── tools/
│   ├── vne-mcp-server/
│   │   └── vne_mcp_server.py    ← MCP 服务端 (16 工具)
│   └── vne-packager/
│       └── vpak.py              ← VPak 打包器
├── custom-nodes/
│   └── dialog_line.lua          ← 合并对话节点
├── engine-patches/
│   └── mcp_host_hotreload.md    ← 热重载补丁
├── skills/                      ← AI 技能
│   ├── void-novel-engine/
│   ├── vne-flow-patterns/
│   ├── vne-scene-recipes/
│   └── vne-custom-extensions/
├── examples/
│   └── _dialog_line_test.flow   ← 测试流
├── README.md
├── README.en.md
└── README.ja.md
```

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)

---

<p align="center">
  <sub>Made with ❤️ for VNE visual novel development</sub>
</p>
