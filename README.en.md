<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/Version-1.2.0-purple?style=for-the-badge" alt="v1.2.0">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-Zero-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.ja.md"><img src="https://img.shields.io/badge/Lang-日本語-blue?style=for-the-badge" alt="日本語"></a>
</p>

# VNE MCP Server

MCP server for VoidNovelEngine. **15 tools**, Python stdlib only, zero dependencies.

Enables AI assistants to read projects, search code, manage assets, validate flows, and monitor console logs.

---

## Installation

Copy the `tools/` directory to your VNE project root:

```
VoidNovelEngine/
├── project.vne
├── application/
├── tools/                        ← place here
│   ├── vne-mcp-server/
│   │   └── vne_mcp_server.py     ← MCP server
│   └── vne-packager/
│       └── vpak.py               ← VPak packager
└── ...
```

```bash
git clone https://github.com/zv163/vne-mcp-server.git
cp -r vne-mcp-server/tools/ /path/to/your/VNE-project/
```

Test:

```bash
python3 tools/vne-mcp-server/vne_mcp_server.py --info
python3 tools/vne-mcp-server/vne_mcp_server.py --list-tools
```

---

## 15 Tools

| # | Tool | Purpose | R/O | Since |
|---|------|---------|:--:|:--:|
| 1 | `vne_project_info` | Project version, asset counts, paths | ✓ | 1.0 |
| 2 | `vne_list_resources` | List resources by type | ✓ | 1.0 |
| 3 | `vne_read_file` | Read project files | ✓ | 1.0 |
| 4 | `vne_list_directory` | Browse directories | ✓ | 1.0 |
| 5 | `vne_search` | Full-text search in Lua scripts | ✓ | 1.0 |
| 6 | `vne_get_resource` | Resource details (incl. .meta) | ✓ | 1.0 |
| 7 | `vne_lua_api` | Engine Lua API reference | ✓ | 1.0 |
| 8 | `vne_export_config` | Export config & VPak status | ✓ | 1.0 |
| 9 | `vne_pack_resources` | Run encrypted VPak packaging | ✗ | 1.0 |
| 10 | `vne_read_vpak` | List/extract .vpak archives | ✓ | 1.0 |
| 11 | `vne_console_log` | Real-time editor console log | ✓ | 1.1 |
| 12 | `vne_refresh_assets` | Refresh asset cache (no restart) | ✗ | **1.2** |
| 13 | `vne_register_asset` | One-click asset registration | ✗ | **1.2** |
| 14 | `vne_validate_flow` | Validate .flow files (crash prevention) | ✓ | **1.2** |
| 15 | `vne_list_node_types` | List all flow node types & pin schemas | ✓ | **1.2** |

---

## v1.2.0 — What's New

Based on real-world usage pain points, v1.2.0 adds 4 tools:

### 1. No more engine restarts

Creating .vns/.flow files externally requires an engine restart to be recognized.

→ `vne_refresh_assets` clears the internal cache and forces a re-read of project.vne.

### 2. Safe asset registration

Manually editing project.vne JSON to register new assets is error-prone.

→ `vne_register_asset` creates .meta + updates project.vne atomically. One call, no mistakes.

### 3. Flow crash prevention

Hand-crafted .flow JSON often has wrong pin keys (e.g. `route_1` instead of `choice_1`) or missing keys on merge_flow inputs — causing the VNE editor to crash on open.

→ `vne_validate_flow` checks JSON structure, pin key correctness, and link integrity. **Always call before opening a generated .flow.**
→ `vne_list_node_types` shows the exact pin schemas for 70+ node types — check before generating.

### Recommended Workflow

```
1. vne_list_node_types     → learn available nodes and pin names
2. Generate .flow file     → via Python script or otherwise
3. vne_validate_flow       → verify no errors
4. vne_register_asset      → auto-register in project
5. vne_refresh_assets      → refresh cache
6. Open in VNE editor      → safe and sound
```

---

## Client Configuration

### Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/path/to/VNE-project/tools/vne-mcp-server/vne_mcp_server.py",
        "--project-path", "/path/to/VNE-project"
      ]
    }
  }
}
```

### Hermes Agent

```bash
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 /path/to/VNE-project/tools/vne-mcp-server/vne_mcp_server.py \
  --project-path /path/to/VNE-project "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh
```

---

## VPak

```bash
python3 tools/vne-packager/vpak.py pack resources/ resources.vpak --key my-key
python3 tools/vne-packager/vpak.py list resources.vpak
python3 tools/vne-packager/vpak.py extract resources.vpak path/to/file --key my-key
```

Encryption: XOR + 256-byte rotating key (SHA256-derived).

---

## Requirements

- Python 3.8+
- VoidNovelEngine project

---

## License

MIT
