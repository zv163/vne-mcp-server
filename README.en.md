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

<h1 align="center">🔧 VNE Tools Collection</h1>
<h3 align="center">VoidNovelEngine Tools Collection — v1.3.0</h3>

<p align="center">
AI-powered visual novel toolkit — MCP server, custom nodes, engine patches, scene templates, skills.
</p>

---

## 📑 Navigation

| Category | Description |
|----------|-------------|
| [📦 Install](#-install) | Requirements + step-by-step |
| [🚀 MCP Tools](#-mcp-tools-16) | 16 tools overview |
| [🧩 Custom Nodes](#-custom-nodes) | `dialog_line` combined dialogue |
| [🔩 Engine Patches](#-engine-patches) | Hot-reload patch |
| [📚 Skills & Pitfalls](#-skills--pitfalls) | AI skills + top 10 pitfalls |
| [📐 Examples](#-examples) | Test flow |

---

## 📦 Install

### Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| **VNE Editor** | 0.1.0-dev.3+ | Must be able to open and run |
| **Python** | 3.8+ | VNE auto-discovers Python from PATH and common install dirs |
| **OS** | Windows | VNE is Windows-only (WSL works for project file access) |
| **Disk** | < 1 MB | Pure text, zero pip dependencies |

The MCP server uses Python **stdlib only** (`json`, `http.server`, `pathlib`). No `pip install` needed.

### Quick Install (3 steps)

```bash
# Step 1: Navigate to your VNE project
cd D:\YourVNEProject\

# Step 2: Clone into tools/
git clone https://github.com/zv163/vne-mcp-server.git tools/vne-mcp-server

# Step 3: Copy custom nodes
cp tools/vne-mcp-server/custom-nodes/dialog_line.lua application/node/custom/
```

### Enable Hot-Reload (optional)

Edit `application/framework/mcp_host.lua` per `engine-patches/mcp_host_hotreload.md`. Adds 22 lines. After this, editing custom nodes no longer requires VNE restart.

### Verify

1. Restart VNE
2. Console should show: `MCP 服务已就绪 http://127.0.0.1:8765`
3. In Hermes Agent: `vne_project_info` → returns project info = success
4. If no MCP log appears, check Python discovery (VNE searches `python.exe` automatically)

### Uninstall

```bash
rm -rf tools/vne-mcp-server/
rm application/node/custom/dialog_line.lua
```

---

## 🚀 MCP Tools (16)

All prefixed `vne_`. Full API docs in `skills/void-novel-engine/references/mcp-api.md`.

### Project Info
`vne_project_info` · `vne_lua_api` · `vne_export_config`

### Resources
`vne_list_resources` · `vne_list_directory` · `vne_get_resource` · `vne_refresh_assets` ★ · `vne_register_asset` ★

### Files
`vne_read_file` · `vne_search`

### Flow
`vne_validate_flow` ★ · `vne_list_node_types`

### VPak
`vne_pack_resources` · `vne_read_vpak`

### Dev & Debug
`vne_console_log` ★ · `vne_reload_custom_nodes` ★★

> ★ = v1.2.0  ·  ★★ = v1.3.0

---

## 🧩 Custom Nodes

### `dialog_line` — Combined Dialogue Line

**File**: `custom-nodes/dialog_line.lua` · **Type**: `dialog_line` · **Category**: Presentation

One node = hide previous + play audio (optional) + show current.

| Pin | Type | Notes |
|-----|------|-------|
| `in` | flow | Input |
| `prev_dialog` | object | Previous dialog_box (optional, chain) |
| `role_text` | string | Character name |
| `dialogue_text` | string | Dialogue text |
| `audio` | audio | Audio (optional, skip if unset) |
| `volume` | float | 0~1, default 0.8 |
| `out` | flow | Output |
| `dialog_box` | object | Current dialog box → next node |

**Chain**: `nodeA.dialog_box → nodeB.prev_dialog`

10 lines drop from ~40 nodes to ~10.

---

## 🔩 Engine Patches

See `engine-patches/mcp_host_hotreload.md`. Insert 22 lines into `mcp_host.lua` update loop.

**Note**: After reload, close/reopen .flow files using custom nodes.

---

## 📚 Skills & Pitfalls

4 AI skills in `skills/`:

| Skill | Content |
|-------|---------|
| `void-novel-engine` | Engine guide: architecture, API, VPak, .flow format, **top 10 pitfalls** |
| `vne-flow-patterns` | Node patterns: dialog lifecycle, branching, foreground, stair layout |
| `vne-scene-recipes` | Ready scene templates: confession, farewell, rooftop |
| `vne-custom-extensions` | Custom node dev: `make_definition` API, `try_check_input` |

### 🔟 Top 10 Pitfalls

> Full details in `skills/void-novel-engine/SKILL.md` → "十大陷阱" section.

| # | Pitfall | Fix |
|---|---------|-----|
| 1 | choice output = `route_1` | `choice_1`~`choice_5` |
| 2 | add_foreground missing shader | psv=2, include shader |
| 3 | merge_flow pins lack key | Avoid this node |
| 4 | >80 nodes per .flow | Split <60/scene |
| 5 | dialog_box no auto-replace | Explicit hide→show chain |
| 6 | hide missing dialog_box link | `hide(fade=0.05)` + `show` dual-link |
| 7 | Same-scene bg change | bg change = switch_scene |
| 8 | choice output = `branch_N` | Use `choice_N` |
| 9 | link pin_id is string | Must be int |
| 10 | Startup crash no error | Clear current_graph_flow_guid |

---

## 📐 Examples

`examples/_dialog_line_test.flow` — 6-node chain demo.

---

## 📄 License

MIT — see [LICENSE](LICENSE)
