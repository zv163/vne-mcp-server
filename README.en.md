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
<h3 align="center">VoidNovelEngine Tools Collection</h3>

<p align="center">
AI-powered visual novel development toolkit — MCP server, custom nodes, engine patches, scene templates, skill library.
<br>
Enables AI assistants to read/write/validate .flow files, hot-reload custom nodes, and generate scenes instantly.
</p>

---

## 📑 Navigation

| Category | Content |
|----------|---------|
| [🚀 MCP Tools](#-mcp-tools-16) | 16 AI-callable tools |
| [🧩 Custom Nodes](#-custom-nodes) | `dialog_line` combined dialogue node |
| [🔩 Engine Patches](#-engine-patches) | mcp_host.lua hot-reload patch |
| [📚 Skill Library](#-skill-library) | 4 AI skills |
| [📐 Examples](#-examples) | Campus romance .flow example |
| [📦 Install](#-install) | Installation guide |
| [🔟 Top 10 Pitfalls](#-top-10-pitfalls) | Common VNE development traps |

---

## 🚀 MCP Tools (16)

16 MCP (Model Context Protocol) tools for AI assistants to operate VNE projects directly.

### Project Info

| Tool | Description |
|------|-------------|
| `vne_project_info` | Project overview (version, asset stats, paths) |
| `vne_lua_api` | VNE Lua API reference |
| `vne_export_config` | Export config (entry flow, VPak status) |

### Resource Management

| Tool | Description |
|------|-------------|
| `vne_list_resources` | List all assets (filterable by type) |
| `vne_list_directory` | List directory contents |
| `vne_get_resource` | Get resource details by GUID |
| `vne_refresh_assets` | Refresh asset cache after external file creation ★ |
| `vne_register_asset` | Atomic asset registration (.meta + project.vne) ★ |

### File Operations

| Tool | Description |
|------|-------------|
| `vne_read_file` | Read project file |
| `vne_search` | Search project file contents |

### Flow Operations

| Tool | Description |
|------|-------------|
| `vne_validate_flow` | Validate .flow files (pin keys, psv, node limits) ★ |
| `vne_list_node_types` | List all node types with pin schemas |

### VPak Packaging

| Tool | Description |
|------|-------------|
| `vne_pack_resources` | Pack resources into encrypted .vpak |
| `vne_read_vpak` | List/extract .vpak contents |

### Debug & Dev

| Tool | Description |
|------|-------------|
| `vne_console_log` | Read VNE editor console logs in real-time ★ |
| `vne_reload_custom_nodes` | Hot-reload custom nodes (no VNE restart) ★★ |

> ★ = added in v1.2.0  |  ★★ = added in v1.3.0

---

## 🧩 Custom Nodes

### `dialog_line` — Combined Dialogue Line

**File**: `custom-nodes/dialog_line.lua` (101 lines)  
**Type ID**: `dialog_line`  
**Category**: Presentation Control

One node = **hide previous + play audio (optional) + show current dialogue**.

```
Traditional (4 nodes):              dialog_line (1 node):
show_dialog_box ──→ hide ──→       ┌─ prev_dialog (optional, chain)
                    play_audio ──→  ├─ role_text
                    show_dialog_box ├─ dialogue_text
                                    ├─ audio (optional, skip if unset)
                                    └─ volume (default 0.8)
```

**Chain connection**: `nodeA.dialog_box` → `nodeB.prev_dialog`

**Impact**: 4 nodes → 1 node. 10 dialogue lines drop from 40 nodes to 10.

---

## 🔩 Engine Patches

### Hot-Reload Patch

**File**: `engine-patches/mcp_host_hotreload.md`  
**Target**: `application/framework/mcp_host.lua`

Adds flag file detection in mcp_host.lua's update loop, working with `vne_reload_custom_nodes`.

**Note**: After reloading, close and reopen .flow files that use custom nodes.

---

## 📚 Skill Library

4 AI skills for Hermes Agent.

| Skill | Description |
|-------|-------------|
| `void-novel-engine` | Complete VNE guide: project structure, API, VPak spec, .flow format |
| `vne-flow-patterns` | Flow node patterns: dialog lifecycle, branches, foreground, generation templates |
| `vne-scene-recipes` | Ready scene templates: classroom confession, cherry tree farewell, rooftop talk |
| `vne-custom-extensions` | Custom node dev guide: `make_definition` API, `try_check_input` usage |

---

## 📐 Examples

`examples/_dialog_line_test.flow` — 6-node test flow demonstrating `dialog_line` chaining.

---

## 📦 Install

```bash
cd YourVNEProject/
git clone https://github.com/zv163/vne-mcp-server.git tools/vne-mcp-server
cp tools/vne-mcp-server/custom-nodes/dialog_line.lua application/node/custom/
# Optional: apply engine patch — see engine-patches/mcp_host_hotreload.md
# Restart VNE — MCP tools auto-available
```

---

## 🔟 Top 10 Pitfalls

Discovered during campus romance VN development:

| # | Pitfall | Fix |
|---|---------|-----|
| 1 | `show_choice_button` output = `route_1` | Use `choice_1`~`choice_5` |
| 2 | `add_foreground` missing `shader` pin | psv=2, include shader |
| 3 | `merge_flow` input pins lack key | Avoid this node |
| 4 | >80 nodes per .flow crashes | Split into scenes |
| 5 | `show_dialog_box` no auto-replace | Explicit `hide_dialog_box` link |
| 6 | Dialog hide/show without link | `hide(fade=0.05)` + `show` dual-link |
| 7 | Same-scene background change | Use `switch_scene`, <60 nodes |
| 8 | Choice pin key mismatch | `show_choice_button` → `choice_1` |
| 9 | link `pin_id` is string | Must be int |
| 10 | Startup crash | Clear invalid `current_graph_flow_guid` |

---

## 📄 License

MIT — see [LICENSE](LICENSE)
