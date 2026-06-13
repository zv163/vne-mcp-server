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
MCP Server · Custom Nodes · Engine Patches · Scene Generator · VPak Packer
</p>

---

## 📑 Navigation

| Section | Description |
|---------|-------------|
| [✨ Features](#-features) | Capability overview |
| [📦 Installation](#-installation) | Three install guides |
| [🔧 Install 1: Tools](#-install-1-tools) | Deploy to VNE project |
| [🔌 Install 2: MCP Clients](#-install-2-mcp-client-setup) | Cursor / Trae / Claude / Hermes |
| [📚 Install 3: Skills](#-install-3-skills) | Hermes Agent skills |
| [🏗️ Repo Structure](#-repo-structure) | Directory layout |

---

## ✨ Features

Complete AI-assisted development toolkit for VoidNovelEngine:

### 🔌 MCP Server — 16 AI Tools

AI assistants can directly operate VNE projects:

- **Project Info**: read config, Lua API reference, export settings
- **Resources**: list/search/register assets, refresh cache
- **Flow Graphs**: validate .flow files (crash prevention), list node types
- **VPak**: encrypt and pack resources, read .vpak contents
- **Debug**: real-time console logs, hot-reload custom nodes

Works with **Cursor**, **Trae**, **Claude Desktop**, **Hermes Agent**, and all MCP-compatible clients.

### 🧩 Custom Nodes

`dialog_line` — merges "hide previous + play audio + show dialogue" into one node. 4 traditional nodes → 1.

### 🔩 Engine Patches

mcp_host.lua hot-reload patch — edit custom nodes without restarting VNE, triggered by AI tool.

### 📚 Skill Library

4 Hermes Agent skills injecting VNE domain knowledge:
- `void-novel-engine` — architecture, API, top 10 pitfalls
- `vne-flow-patterns` — node connection patterns & layout rules
- `vne-scene-recipes` — campus romance scene templates
- `vne-custom-extensions` — custom node development guide

---

## Overview

| Component | Description |
|-----------|-------------|
| `tools/vne-mcp-server/` | MCP server, 16 AI tools |
| `tools/vne-packager/` | VPak resource packer |
| `custom-nodes/` | Custom nodes (dialog_line, etc.) |
| `engine-patches/` | Engine patches (hot-reload, etc.) |
| `skills/` | Hermes Agent skills |
| `examples/` | Test flows |

---

## 📦 Installation

Three guides for different components:

| Guide | For | Link |
|-------|-----|------|
| 🔧 **Tools** | All users — deploy to VNE project | [→](#-install-1-tools) |
| 🔌 **MCP Clients** | AI assistant users — Cursor / Trae / Claude / Hermes | [→](#-install-2-mcp-client-setup) |
| 📚 **Skills** | Hermes Agent users — load VNE skills | [→](#-install-3-skills) |

---

## 🔧 Install 1: Tools

### Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| VNE Editor | 0.1.0-dev.3+ | Running and stable |
| Python | 3.8+ | Auto-discovered by VNE |
| Git | Any | For cloning |
| OS | Windows | VNE is Windows-only |

Zero pip dependencies — stdlib only.

### Steps

```bash
cd D:\YourVNEProject\
git clone https://github.com/zv163/vne-mcp-server.git tools/vne-mcp-server
cp tools/vne-mcp-server/custom-nodes/dialog_line.lua application/node/custom/
# Restart VNE
```

### Verify

Console shows:
```
MCP 服务已就绪 http://127.0.0.1:8765
```

### Enable Hot-Reload (optional)

Edit `application/framework/mcp_host.lua` per `engine-patches/mcp_host_hotreload.md`.

### Uninstall

```bash
rm -rf tools/vne-mcp-server/
rm application/node/custom/dialog_line.lua
```

---

## 🔌 Install 2: MCP Client Setup

VNE MCP server runs at `127.0.0.1:8765` via HTTP/SSE.

```
Transport: SSE (HTTP)
Server:    http://127.0.0.1:8765
SSE:       http://127.0.0.1:8765/sse
Messages:  http://127.0.0.1:8765/message
```

> MCP server starts automatically with VNE. No manual launch needed.

---

### Cursor

Edit `~/.cursor/mcp.json`:

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

---

### Trae

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

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

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

Or stdio mode:

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

In `config.yaml`:

```yaml
mcp:
  servers:
    - name: vne
      transport: sse
      url: http://127.0.0.1:8765/sse
```

Or via CLI:

```bash
hermes mcp add vne --transport sse --url http://127.0.0.1:8765/sse
```

---

### Verify MCP

Run in your AI assistant:

```
vne_project_info
```

Returns project info = connected.

---

## 📚 Install 3: Skills

Skills are Hermes Agent domain knowledge modules. 4 skills included.

### Setup

```bash
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

### Skill List

| Skill | Purpose |
|-------|---------|
| `void-novel-engine` | Engine guide: architecture, API, VPak, pitfalls |
| `vne-flow-patterns` | Node patterns: dialog, branch, foreground, layout |
| `vne-scene-recipes` | Scene templates: classroom, sakura, rooftop |
| `vne-custom-extensions` | Custom node dev: API, try_check_input |

Skills auto-load when AI handles VNE tasks.

---

## 🏗️ Repo Structure

```
vne-mcp-server/
├── tools/vne-mcp-server/vne_mcp_server.py
├── tools/vne-packager/vpak.py
├── custom-nodes/dialog_line.lua
├── engine-patches/mcp_host_hotreload.md
├── skills/{void-novel-engine,vne-flow-patterns,vne-scene-recipes,vne-custom-extensions}/
├── examples/_dialog_line_test.flow
├── README.md / README.en.md / README.ja.md
└── LICENSE (MIT)
```

---

## 📄 License

MIT — see [LICENSE](LICENSE)
