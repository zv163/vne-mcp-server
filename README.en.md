<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2024--11--05-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-Zero-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.ja.md"><img src="https://img.shields.io/badge/Lang-日本語-white?style=for-the-badge" alt="日本語"></a>
</p>

# VNE MCP Server

**MCP (Model Context Protocol) server for VoidNovelEngine.** Enables AI assistants (Claude, GPT, Cursor, etc.) to read, search, package, and debug VNE projects directly. 11 tools, pure Python stdlib, zero external dependencies.

Two transport modes: **Stdio** (for Claude Desktop / Cursor) and **TCP/HTTP SSE** (embedded inside the VNE editor).

---

## 11 Tools

| # | Tool | Description | R/O |
|---|------|-------------|:---:|
| 1 | `vne_project_info` | Project overview — version, asset counts, paths | ✓ |
| 2 | `vne_list_resources` | List resources by type (texture, audio, flow, etc.) | ✓ |
| 3 | `vne_read_file` | Read any project file by relative path | ✓ |
| 4 | `vne_list_directory` | Browse project directory contents | ✓ |
| 5 | `vne_search` | Full-text search in Lua scripts (case-insensitive) | ✓ |
| 6 | `vne_get_resource` | Resource detail by GUID (includes .meta content) | ✓ |
| 7 | `vne_lua_api` | Engine Lua API reference — modules, classes, resource types | ✓ |
| 8 | `vne_export_config` | View export settings — title, entry flow, VPak status | ✓ |
| 9 | `vne_pack_resources` | Run VPak resource packaging (XOR encryption + zlib) | ✗ |
| 10 | `vne_read_vpak` | List / extract files from .vpak archives | ✓ |
| 11 | `vne_console_log` | Real-time VNE editor console log reader | ✓ |

---

## Quick Start

```bash
# Test: show project info
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine --info

# Test: list all textures
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine --resources texture

# Test: show all available tools
python vne_mcp_server.py --list-tools
```

### Stdio Mode (default)

```bash
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine
```

### TCP/HTTP Mode (embedded in VNE editor)

```bash
python vne_mcp_server.py --project-path /path/to/VoidNovelEngine --port 8765
```

Endpoints after launch:

| Endpoint | Purpose |
|----------|---------|
| `http://127.0.0.1:8765/sse` | SSE push channel |
| `http://127.0.0.1:8765/message` | Message receiver |
| `http://127.0.0.1:8765/health` | Health check |

---

## Client Configuration

### Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vne": {
      "command": "python",
      "args": [
        "/path/to/vne-mcp-server/vne_mcp_server.py",
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
# Create wrapper script
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 /path/to/vne-mcp-server/vne_mcp_server.py \
  --project-path /path/to/VoidNovelEngine "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh

# Register with Hermes
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh
```

### Generic MCP Client

```json
{
  "mcpServers": {
    "vne": {
      "command": "python",
      "args": ["vne_mcp_server.py", "--project-path", "/path/to/VoidNovelEngine"]
    }
  }
}
```

---

## TCP Mode & VNE Editor Integration

The VNE editor includes a built-in Lua MCP host (`mcp_host.lua`) that, on startup:

1. Auto-discovers Python on Windows
2. Launches `vne_mcp_server.py --port 8765` as a child process
3. Watches stdout for `VNE_MCP_READY` signal
4. Opens SSE connection for real-time event streaming
5. Bridges `LogManager.log()` output → `save/diagnostics/mcp_console.jsonl`

This enables the **`vne_console_log`** tool — AI assistants can read the VNE editor console in near-real-time.

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

## VPak Integration

Two tools interact with VPak encrypted archives:

- **`vne_pack_resources`** — spawns `vpak.py pack` as subprocess (XOR encryption, optional zlib)
- **`vne_read_vpak`** — imports `vpak.py` directly to list / extract files

`vpak.py` can also be used standalone:

```bash
# Pack resources
python vpak.py pack application/resources application/resources.vpak --key my-key

# List archive contents
python vpak.py list application/resources.vpak

# Extract a file
python vpak.py extract application/resources.vpak texture/icon.png --key my-key
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

Encryption: XOR cipher with 256-byte rotating key (derived from SHA256 + deterministic scrambling)

---

## File Structure

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

## Requirements

- **Python 3.8+** — stdlib only, no pip install needed
- A VoidNovelEngine project (contains `project.vne`)

---

## Links

- [VoidNovelEngine](https://github.com/VoidmatrixHeathcliff/VoidNovelEngine) — the visual novel engine
- [Model Context Protocol](https://modelcontextprotocol.io) — MCP specification
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — self-improving AI agent

---

## License

MIT — see [LICENSE](LICENSE)
