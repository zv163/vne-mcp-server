<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-Zero-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.ja.md"><img src="https://img.shields.io/badge/Lang-日本語-white?style=for-the-badge" alt="日本語"></a>
</p>

# VNE MCP Server

**MCP (Model Context Protocol) server for VoidNovelEngine.** Enables AI assistants to read, search, package, and debug VNE projects. 11 tools, pure Python stdlib, zero external dependencies.

---

## Table of Contents

- [📦 Installation & File Placement](#-installation--file-placement)
- [🛠 11 Tools](#-11-tools)
- [🚀 Quick Start](#-quick-start)
- [🔧 Client Configuration](#-client-configuration)
  - [Claude Desktop](#claude-desktop)
  - [Cursor / Windsurf](#cursor--windsurf)
  - [Hermes Agent](#hermes-agent)
  - [Generic MCP Client](#generic-mcp-client)
- [🔗 TCP Mode & Editor Integration](#-tcp-mode--vne-editor-integration)
- [🔐 VPak Integration](#-vpak-integration)
- [📁 File Structure](#-file-structure)
- [📋 Requirements](#-requirements)
- [🔗 Links](#-links)

---

## 📦 Installation & File Placement

### What's in the box

This repository contains **two Python files** — both required:

| File | Purpose | Required |
|------|---------|:---:|
| `vne_mcp_server.py` | MCP server main program (11 tools) | ✓ Required |
| `vpak.py` | VPak pack/unpack module | ✓ Required |

The `vne_pack_resources` and `vne_read_vpak` tools call into `vpak.py`, so **both files must live in the same directory**.

### Setup

```bash
# 1. Clone to your home directory (recommended)
git clone https://github.com/zv163/vne-mcp-server.git ~/vne-mcp-server

# 2. Verify the files
ls ~/vne-mcp-server/
# Output: vne_mcp_server.py  vpak.py  README.md  LICENSE

# 3. Check Python version (3.8+)
python3 --version

# 4. Smoke test
python3 ~/vne-mcp-server/vne_mcp_server.py --list-tools
```

> **Path tip:** Keep it in `~/vne-mcp-server/` or any fixed location. Do NOT place it inside a VNE project — this is a standalone tool that can serve multiple VNE projects.

### Layout Overview

```
~/vne-mcp-server/              ← Recommended install location
├── vne_mcp_server.py          ← MCP server (required)
├── vpak.py                    ← VPak module (must be same dir)
├── README.md / .en.md / .ja.md
└── LICENSE

/path/to/VoidNovelEngine/      ← Your VNE project (anywhere)
├── project.vne
├── application/
│   ├── resources/
│   ├── framework/
│   └── scene/
└── save/diagnostics/
```

---

## 🛠 11 Tools

| # | Tool | Description | R/O |
|---|------|-------------|:---:|
| 1 | `vne_project_info` | Project overview — version, asset counts, paths | ✓ |
| 2 | `vne_list_resources` | List resources by type (texture, audio, flow, etc.) | ✓ |
| 3 | `vne_read_file` | Read any project file by relative path | ✓ |
| 4 | `vne_list_directory` | Browse project directory contents | ✓ |
| 5 | `vne_search` | Full-text search in Lua scripts (case-insensitive) | ✓ |
| 6 | `vne_get_resource` | Resource detail by GUID (includes .meta) | ✓ |
| 7 | `vne_lua_api` | Engine Lua API reference — modules, classes, types | ✓ |
| 8 | `vne_export_config` | Export settings — title, entry flow, VPak status | ✓ |
| 9 | `vne_pack_resources` | Run VPak packaging (XOR encryption + zlib) | ✗ |
| 10 | `vne_read_vpak` | List / extract files from .vpak archives | ✓ |
| 11 | `vne_console_log` | Real-time editor console log reader | ✓ |

---

## 🚀 Quick Start

```bash
# Show project info
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine --info

# List all textures
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine --resources texture

# Show available tools
python3 ~/vne-mcp-server/vne_mcp_server.py --list-tools
```

### Stdio Mode (default, for MCP clients)

```bash
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine
```

### TCP/HTTP Mode (embedded in VNE editor)

```bash
python3 ~/vne-mcp-server/vne_mcp_server.py --project-path /path/to/VoidNovelEngine --port 8765
```

| Endpoint | Purpose |
|----------|---------|
| `http://127.0.0.1:8765/sse` | SSE push channel |
| `http://127.0.0.1:8765/message` | Message receiver |
| `http://127.0.0.1:8765/health` | Health check |

---

## 🔧 Client Configuration

> **Note:** Replace `/path/to/vne-mcp-server/` with your actual install path (e.g. `~/vne-mcp-server`).

### Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/home/yourname/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/path/to/VoidNovelEngine"
      ]
    }
  }
}
```

### Cursor / Windsurf

Same JSON format — add to your MCP configuration file.

### Hermes Agent

```bash
# 1. Create wrapper script
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 ~/vne-mcp-server/vne_mcp_server.py \
  --project-path /path/to/VoidNovelEngine "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh

# 2. Register with Hermes
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh

# 3. Verify
hermes mcp list | grep vne
```

> **Note:** If `hermes mcp add` fails with an unrecognized `--project-path` flag, use the wrapper script approach above — don't let hermes pass `--project-path` directly.

### Generic MCP Client

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

## 🔗 TCP Mode & VNE Editor Integration

The VNE editor includes a Lua MCP host (`mcp_host.lua`) that, on startup:

1. Auto-discovers Python on the system
2. Launches `vne_mcp_server.py --port 8765` as a child process
3. Waits for `VNE_MCP_READY` signal
4. Opens SSE connection for real-time events
5. Bridges `LogManager.log()` output → `save/diagnostics/mcp_console.jsonl`

This powers the **`vne_console_log`** tool — near-real-time editor console access for AI.

```
┌─────────────────────────┐
│     AI Assistant         │
│  (Claude / GPT / Cursor) │
└─────┬───────────────────┘
      │ MCP (stdio / HTTP SSE)
┌─────▼───────────────────┐
│   vne_mcp_server.py      │
│  ┌─────────────────────┐ │
│  │  MCP Protocol Layer  │ │
│  │  (JSON-RPC 2.0)     │ │
│  ├─────────────────────┤ │
│  │  VNEProject Core     │ │
│  │  · project.vne parse │ │
│  │  · asset index       │ │
│  │  · file I/O          │ │
│  │  · full-text search  │ │
│  ├─────────────────────┤ │
│  │  VPak Module         │ │
│  │  · vpak.py subprocess│ │
│  ├─────────────────────┤ │
│  │  Console Bridge      │ │
│  │  · jsonl reader      │ │
│  └─────────────────────┘ │
└─────┬───────────────────┘
      │ file read / subprocess
┌─────▼───────────────────┐
│  VNE Project             │
│  ├── project.vne        │
│  ├── application/       │
│  │   ├── resources/     │
│  │   ├── framework/     │
│  │   └── scene/         │
│  └── save/diagnostics/  │
└─────────────────────────┘
```

---

## 🔐 VPak Integration

- **`vne_pack_resources`** — spawns `vpak.py pack` subprocess (XOR encryption, optional zlib)
- **`vne_read_vpak`** — imports `vpak.py` module to list / extract files

`vpak.py` can also be used standalone:

```bash
# Pack
python3 ~/vne-mcp-server/vpak.py pack  resources/  resources.vpak --key my-key

# List
python3 ~/vne-mcp-server/vpak.py list  resources.vpak

# Extract
python3 ~/vne-mcp-server/vpak.py extract  resources.vpak  texture/icon.png --key my-key
```

### VPak Format

| Section | Size | Description |
|---------|------|-------------|
| Magic | 4 bytes | `VPAK` |
| Version | 4 bytes | uint32 LE |
| Flags | 4 bytes | bit0=encrypted, bit1=compressed |
| File Count | 4 bytes | uint32 LE |
| File Table | N×32 bytes | path hash + offset + size |
| Data | N bytes | concatenated file data |

Encryption: XOR cipher with 256-byte rotating key (SHA256 + deterministic scrambling)

---

## 📁 File Structure

```
vne-mcp-server/
├── vne_mcp_server.py   # Main server (1118 lines, 11 tools)
├── vpak.py             # VPak packager (316 lines, XOR + zlib)
├── README.md           # Chinese (default)
├── README.en.md        # English (this file)
├── README.ja.md        # Japanese
└── LICENSE             # MIT
```

---

## 📋 Requirements

- **Python 3.8+** — stdlib only, no pip install needed
- A VoidNovelEngine project (contains `project.vne`)

---

## 🔗 Links

- [VoidNovelEngine](https://github.com/VoidmatrixHeathcliff/VoidNovelEngine) — the visual novel engine
- [Model Context Protocol](https://modelcontextprotocol.io) — MCP specification
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — self-improving AI agent

---

## License

MIT — see [LICENSE](LICENSE)
