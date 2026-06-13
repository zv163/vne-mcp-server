<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/MCP-2025--11--25-green?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Deps-Zero-orange?style=for-the-badge" alt="Zero Dependencies">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.ja.md"><img src="https://img.shields.io/badge/Lang-日本語-white?style=for-the-badge" alt="日本語"></a>
</p>

# VNE MCP Server

MCP server for VoidNovelEngine. 11 tools, pure Python stdlib, zero dependencies.

---

## Table of Contents

- [Installation](#installation)
- [11 Tools](#11-tools)
- [Client Configuration](#client-configuration)
- [VPak](#vpak)

---

## Installation

Drop the `tools/` folder into your VNE project root:

```
VoidNovelEngine/
├── project.vne
├── application/
├── tools/                        ← here
│   ├── vne-mcp-server/
│   │   └── vne_mcp_server.py     ← MCP server
│   └── vne-packager/
│       └── vpak.py               ← VPak packager
└── ...
```

```bash
# Option 1: clone & copy
git clone https://github.com/zv163/vne-mcp-server.git
cp -r vne-mcp-server/tools/ your-vne-project/

# Option 2: download ZIP, extract, copy tools/ over
```

Test:

```bash
python3 tools/vne-mcp-server/vne_mcp_server.py --info
python3 tools/vne-mcp-server/vne_mcp_server.py --list-tools
```

---

## 11 Tools

| # | Tool | Description | R/O |
|---|------|-------------|:--:|
| 1 | `vne_project_info` | Project version, asset counts, paths | ✓ |
| 2 | `vne_list_resources` | List resources by type | ✓ |
| 3 | `vne_read_file` | Read project files | ✓ |
| 4 | `vne_list_directory` | Browse directories | ✓ |
| 5 | `vne_search` | Full-text search in Lua scripts | ✓ |
| 6 | `vne_get_resource` | Resource detail by GUID (incl. .meta) | ✓ |
| 7 | `vne_lua_api` | Engine Lua API reference | ✓ |
| 8 | `vne_export_config` | Export settings & VPak status | ✓ |
| 9 | `vne_pack_resources` | Run encrypted resource packaging | ✗ |
| 10 | `vne_read_vpak` | List / extract .vpak files | ✓ |
| 11 | `vne_console_log` | Real-time editor console log | ✓ |

---

## Client Configuration

### Claude Desktop

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/your-vne-project/tools/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/your-vne-project"
      ]
    }
  }
}
```

### Cursor / Windsurf

Same format.

### Hermes Agent

```bash
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 /your-vne-project/tools/vne-mcp-server/vne_mcp_server.py \
  --project-path /your-vne-project "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh
```

### Other Clients

```json
{
  "mcpServers": {
    "vne": {
      "command": "python3",
      "args": [
        "/your-vne-project/tools/vne-mcp-server/vne_mcp_server.py",
        "--project-path",
        "/your-vne-project"
      ]
    }
  }
}
```

---

## VPak

`vne_pack_resources` and `vne_read_vpak` depend on `tools/vne-packager/vpak.py`. Standalone usage:

```bash
# Pack
python3 tools/vne-packager/vpak.py pack resources/ resources.vpak --key my-key

# List
python3 tools/vne-packager/vpak.py list resources.vpak

# Extract
python3 tools/vne-packager/vpak.py extract resources.vpak path/to/file --key my-key
```

Encryption: XOR + 256-byte rotating key (SHA256-derived)

---

## Requirements

- Python 3.8+
- A VoidNovelEngine project

---

## License

MIT
