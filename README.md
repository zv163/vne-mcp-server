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
AI 驱动的视觉小说开发工具集 — 让 AI 助手能读写校验 .flow、热重载自定义节点、一键生成场景。
</p>

---

## 📑 导航

| 分类 | 说明 |
|------|------|
| [📦 安装](#-安装) | 环境要求 + 分步安装 |
| [🚀 MCP 工具](#-mcp-工具-16-个) | 16 个工具速览 |
| [🧩 自定义节点](#-自定义节点) | `dialog_line` 合并对话行 |
| [🔩 引擎补丁](#-引擎补丁) | 热重载补丁 |
| [📚 技能与陷阱](#-技能与陷阱) | AI 技能 + 十大陷阱速查 |
| [📐 示例](#-示例) | 测试流 |

---

## 📦 安装

### 环境要求

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| **VNE 编辑器** | 0.1.0-dev.3+ | 项目必须能正常打开 |
| **Python** | 3.8+ | VNE 会自动检测 PATH 和常见安装目录下的 Python |
| **操作系统** | Windows | VNE 仅支持 Windows（WSL 下通过 /mnt/ 访问项目文件） |
| **磁盘空间** | < 1 MB | 纯文本工具集，无额外依赖 |

Python 无需安装 pip 包，MCP 服务端仅使用 Python **标准库**（`json`, `http.server`, `pathlib` 等）。

### 快速安装（3 步）

```bash
# 步骤 1: 进入 VNE 项目目录
cd D:\YourVNEProject\     # Windows
# 或 WSL 下:
cd /mnt/d/YourVNEProject/

# 步骤 2: 克隆工具集到 tools/ 目录
git clone https://github.com/zv163/vne-mcp-server.git tools/vne-mcp-server

# 步骤 3: 复制自定义节点到 VNE 项目
cp tools/vne-mcp-server/custom-nodes/dialog_line.lua application/node/custom/
```

### 启用热重载（可选）

编辑 `application/framework/mcp_host.lua`，按 `engine-patches/mcp_host_hotreload.md` 中的说明添加 22 行代码。启用后改自定义节点无需重启 VNE。

### 验证安装

1. 重启 VNE 编辑器
2. 查看控制台输出，应出现：
   ```
   MCP 服务已就绪 http://127.0.0.1:8765
   ```
3. 在 Hermes Agent 中执行 `vne_project_info`，返回项目信息即成功
4. 如果 VNE 启动后没有 MCP 日志，检查 Python 是否可被 VNE 发现（VNE 会自动搜索 `python.exe`）

### 卸载

```bash
# 删除 tools 目录即可
rm -rf tools/vne-mcp-server/
# 删除自定义节点
rm application/node/custom/dialog_line.lua
```

---

## 🚀 MCP 工具 (16 个)

所有工具前缀 `vne_`，AI 助手可直接调用。完整 API 文档见 `skills/void-novel-engine/references/mcp-api.md`。

### 项目信息
`vne_project_info` · `vne_lua_api` · `vne_export_config`

### 资源管理
`vne_list_resources` · `vne_list_directory` · `vne_get_resource` · `vne_refresh_assets` ★ · `vne_register_asset` ★

### 文件操作
`vne_read_file` · `vne_search`

### 流图校验
`vne_validate_flow` ★ · `vne_list_node_types`

### VPak 打包
`vne_pack_resources` · `vne_read_vpak`

### 调试开发
`vne_console_log` ★ · `vne_reload_custom_nodes` ★★

> ★ = v1.2.0 新增  ·  ★★ = v1.3.0 新增

---

## 🧩 自定义节点

### `dialog_line` — 合并对话行

**文件**: `custom-nodes/dialog_line.lua` · **类型**: `dialog_line` · **分类**: 演出控制

一个节点完成「隐藏上一句 + 播放音频(可选) + 显示当前对话」。

```
传统: show → hide → play_audio → show  (4 节点)
现在: dialog_line  (1 节点)
```

| 引脚 | 类型 | 说明 |
|------|------|------|
| `in` | flow | 流程输入 |
| `prev_dialog` | object | 上一句的 dialog_box（可选，链式连接） |
| `role_text` | string | 角色名 |
| `dialogue_text` | string | 台词内容 |
| `audio` | audio | 音频（可选，无则跳过） |
| `volume` | float | 音量 (0~1，默认 0.8) |
| `out` | flow | 流程输出 |
| `dialog_box` | object | 当前对话框对象（连接下一节点） |

**链式用法**: `nodeA.dialog_box → nodeB.prev_dialog`

效果：10 句对话从 ~40 节点降到 ~10 节点。

---

## 🔩 引擎补丁

### mcp_host.lua 热重载补丁

详见 `engine-patches/mcp_host_hotreload.md`。

在 `mcp_host.lua` 的 update 循环中插入 22 行代码，配合 `vne_reload_custom_nodes` 实现自定义节点热重载。

```
MCP 工具写 flag → VNE 每帧检测 → definition_loader.load() → 写 result → MCP 工具读回
```

**注意**：重载后需关闭并重新打开使用自定义节点的 .flow 文件。

---

## 📚 技能与陷阱

4 个 AI 技能（位于 `skills/`），供 Hermes Agent 加载：

| 技能 | 内容 |
|------|------|
| `void-novel-engine` | 引擎全面指南：架构、API、VPak、.flow 格式、**十大陷阱** |
| `vne-flow-patterns` | 节点连接模式：对话框生命周期、分支、前景图、楼梯布局 |
| `vne-scene-recipes` | 即用场景模板：教室表白、樱花告别、天台谈心 |
| `vne-custom-extensions` | 自定义节点开发：`make_definition` API、`try_check_input` |

### 🔟 十大陷阱速查

> 完整版见 `skills/void-novel-engine/SKILL.md` 文末「十大陷阱」章节。

| # | 陷阱 | 正确做法 |
|---|------|---------|
| 1 | choice 输出 key = `route_1` | `choice_1`~`choice_5` |
| 2 | add_foreground 缺 shader pin | psv=2，含 shader |
| 3 | merge_flow pin 缺 key | 避免使用 |
| 4 | 单 .flow > 80 节点 | 拆分 < 60 节点/场景 |
| 5 | dialog_box 不自动替换 | 显式 hide → show 链 |
| 6 | hide 无 dialog_box 链接 | `hide(fade=0.05)` + `show` 双链接 |
| 7 | 同场景换背景 | 换背景 = switch_scene |
| 8 | choice 输出 key = `branch_N` | 用 `choice_N` |
| 9 | link pin_id 是 string | 必须 int |
| 10 | 启动崩溃无报错 | 清 current_graph_flow_guid |

---

## 📐 示例

`examples/_dialog_line_test.flow` — 6 节点测试流：

```
entry → set_style → dialog_line(张晨) → dialog_line(小美+BGM) → dialog_line(林雪) → 菜单
```

---

## 🏗️ 仓库结构

```
vne-mcp-server/
├── tools/vne-mcp-server/vne_mcp_server.py   ← MCP 服务端 (16 工具)
├── tools/vne-packager/vpak.py               ← VPak 打包器
├── custom-nodes/dialog_line.lua             ← 合并对话节点
├── engine-patches/mcp_host_hotreload.md     ← 热重载补丁
├── skills/                                  ← AI 技能库
│   ├── void-novel-engine/                   ← 引擎指南 + 十大陷阱
│   ├── vne-flow-patterns/                   ← 流图模式
│   ├── vne-scene-recipes/                   ← 场景模板
│   └── vne-custom-extensions/               ← 自定义节点开发
├── examples/_dialog_line_test.flow          ← 测试流
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
