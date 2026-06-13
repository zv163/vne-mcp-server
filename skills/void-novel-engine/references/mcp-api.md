# VNE MCP Server API Reference

## Transport

Stdio JSON-RPC 2.0. Each message is one JSON object per line. Protocol version `2025-11-25`.

TCP/HTTP SSE mode available via `--port 8765` (SSE: `/sse`, Message: `/message`, Health: `/health`).

The `initialize` response includes an `instructions` field (since protocol 2025-11-25) that gives LLM clients a hint about how to use the server:
```
"instructions": "VNE MCP Server — provides 16 tools for VoidNovelEngine projects.
Use vne_project_info first to get an overview, vne_search for code lookup,
vne_console_log for editor diagnostics."
```

## Tools

### vne_project_info

Get project overview: version, asset counts by type, paths.

Input: `{}`

Output:
```json
{
  "project_path": "/path/to/project",
  "project_version": "0.1.0-dev.3",
  "total_assets": 33,
  "resource_counts": {"font": 2, "flow": 12, "texture": 6, ...},
  "application_path": "...",
  "resources_path": "..."
}
```

### vne_list_resources

List all resources, optionally filtered by type.

Input: `{"type": "texture"}`  (omit `type` for all)

Output: Array of `{guid, type, relative_path, meta_path, size}`

### vne_read_file

Read a project file by relative path.

Input: `{"path": "main.lua"}`
Output: File content as text, or "File not found: ..."

### vne_list_directory

List directory contents.

Input: `{"path": "application/framework"}`  (default: ".")
Output: Array of `{name, type, size}`

### vne_search

Case-insensitive search in project files.

Input: `{"query": "VPakLoader", "file_pattern": "*.lua"}`
Output: Array of `{file, line, content}` (max 50 results)

### vne_get_resource

Get resource detail by GUID, including parsed .meta content.

Input: `{"guid": "39d13340-4d81-420a-9637-7440058af6f5"}`
Output: `{asset: {...}, meta_content: {...}}`

### vne_lua_api

Get engine Lua module reference and project structure.

Input: `{}`
Output: JSON with `engine_modules`, `key_modules`, `project_structure`, `resource_types`

### vne_export_config

Get export configuration from project.vne.

Input: `{}`
Output: `{title, entry_flow_guid, default_fullscreen, single_file, developer, ...}`

### vne_pack_resources

Run VPak packaging via Python subprocess.

Input: `{"source_dir": "application/resources", "output": "application/resources.vpak", "key": "my-key", "compress": false}`
Output: Subprocess stdout/stderr or error

### vne_read_vpak

List or extract from VPak archives.

Input:
```json
{"archive": "application/resources.vpak", "action": "list"}
{"archive": "application/resources.vpak", "action": "extract", "file_path": "texture/icon.png", "key": "my-key"}
```
Output: Entry list or file data (text or base64 for binary)

### vne_console_log

Read the VNE editor's real-time console output. Requires the MCP Console Bridge
(mcp_host.lua) to be running — this is built into the VNE editor since the MCP
host was added. The bridge wraps LogManager.log() and writes entries to
`save/diagnostics/mcp_console.jsonl` (max 500 entries, flushed every 1s).

Input:
```json
{"limit": 50}                           // default: 50, max: 500
{"level": "error"}                      // filter: info|warning|error|success|debug
{"since": 100}                          // entries with index >= since
```
Output:
```json
{
  "status": "ok",
  "total_lines": 342,
  "returned": 50,
  "parse_errors": 0,
  "log_file": "/path/to/save/diagnostics/mcp_console.jsonl",
  "file_size": 12345,
  "entries": [
    {"time": "[2026-06-13 12:30:00]", "level": "info", "msg": "..."},
    ...
  ]
}
```

When VNE editor is not running or the bridge hasn't started:
```json
{"status": "no_log_file", "hint": "...", "expected_path": "..."}
```

### vne_refresh_assets (NEW in 1.2.0)

Clear the MCP server's internal cache and force re-reading project.vne from disk.
Use after creating/modifying .vns, .flow, .meta files or editing project.vne
externally. Eliminates the need to restart the VNE editor.

Input: `{}`

Output:
```json
{
  "status": "refreshed",
  "message": "Asset cache cleared. Project re-loaded.",
  "total_assets": 35,
  "resource_counts": {"flow": 14, ...}
}
```

### vne_register_asset (NEW in 1.2.0)

Atomically register a new asset file: creates the .meta file, generates a GUID,
adds it to project.vne's asset_registry, and optionally adds to open_flow_guid_list.
Use this instead of manually editing project.vne JSON.

Input:
```json
{
  "path": "flow/校园恋爱.flow",
  "type": "flow",
  "add_to_open_flows": true
}
```
Output:
```json
{
  "status": "registered",
  "guid": "c34f4ec4-...",
  "relative_path": "flow/校园恋爱.flow",
  "type": "flow",
  "meta_path": "application/resources/flow/校园恋爱.flow.meta",
  "size": 84713,
  "mtime": 1781339128
}
```

### vne_validate_flow (NEW in 1.2.0, enhanced in 1.2.1)

Validate a .flow file for structural correctness before opening in VNE editor.
Checks: valid JSON, correct pin keys (especially choice_N for show_choice_button),
merge_flow input keys, missing pin keys, broken link references.

**v1.2.1 additions:**
- Detects non-integer pin IDs in links (common bug: passing dicts like `{'in': 177}` instead of `177`)
- Warns when node count exceeds 80 (VNE editor hard limit)

**CRITICAL: Always call this after generating .flow files and before opening them
in the VNE editor.** Prevents crashes from wrong pin keys.

Input: `{"path": "application/resources/flow/校园恋爱.flow"}`

Output:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "node_count": 127,
  "link_count": 129,
  "known_node_types": 70
}
```

Common errors caught:
- `show_choice_button` output key `route_1` should be `choice_1`
- `merge_flow` input pin missing 'key' → causes crash
- Link references non-existent pin IDs

### vne_list_node_types (NEW in 1.2.0)

List all available flow node type_ids with their pin schemas (inputs/outputs).
Scans `application/node/builtin/` to discover 70+ node types.

**Use before generating .flow files to ensure correct pin keys.**

Input: `{}`

Output:
```json
[
  {
    "type_id": "show_dialog_box",
    "name": "显示对话框",
    "category": "演出控制",
    "inputs": [
      {"key": "in", "type_id": "flow", "name": ""},
      {"key": "role_text", "type_id": "string", "name": "角色文本"},
      ...
    ],
    "outputs": [
      {"key": "out", "type_id": "flow", "name": ""},
      {"key": "dialog_box", "type_id": "object", "name": "对话框"}
    ]
  },
  ...
]
```

## Flow Generation Best Practices

When generating .flow files programmatically:

1. Call `vne_list_node_types` first to see correct pin keys for each node type
2. Generate the .flow JSON
3. Call `vne_validate_flow` — fix any errors before proceeding
4. If validation passes, call `vne_register_asset` to register
5. Call `vne_refresh_assets` so the editor sees the new file
6. Open in VNE editor

### Dialog Lifecycle (CRITICAL)

`show_dialog_box` creates **independent objects** that stack. Between every pair:
- Insert `hide_dialog_box` with TWO connections: flow AND dialog_box object
- Without the object connection, hide_dialog_box has no target

### Known Pitfall Pin Keys

| Node Type | Wrong Key | Correct Key | Crash? |
|-----------|-----------|-------------|:--:|
| `show_choice_button` output | `route_1`, `route_2`, `route_3` | `choice_1`, `choice_2`, `choice_3` | **YES** |
| `merge_flow` input | (missing key) | Needs explicit key | **YES** |
| Any link pin ID | dict (e.g. `{'in': 177}`) | int (e.g. `177`) | **YES** |
| `switch_background` | pin_schema_version: 1 | pin_schema_version: **2** | Warning |
| `add_foreground` → `remove_foreground` | Not connected | Link foreground output → foreground input | Runtime |
| Any .flow file | >80 nodes | Split into multiple scenes | **YES** (freeze/crash) |
| `add_foreground` → `remove_foreground` | Not connected | Link foreground output → foreground input | Runtime |

**Critical**: When generating links programmatically, ensure `L(from_pin, to_pin)` receives integer pin IDs, not dicts. A common bug is passing `N()`'s return maps directly — e.g. `L(f, di)` where `di` is `{'in': 177, 'seconds': 178}` instead of `di['in']`. This causes an immediate VNE editor crash with no error message.

### VNE Editor Startup Crash Recovery

If VNE crashes on startup, check `project.vne`:
- `current_graph_flow_guid` may point to a large/corrupt .flow file
- Reset it to a known-working flow GUID (e.g. `主菜单.flow`)
- Trim `open_flow_guid_list` to remove problematic entries

```python
# Recovery script
proj['current_flow_guid'] = safe_guid      # e.g. 主菜单.flow
proj['current_graph_flow_guid'] = safe_guid
proj['open_flow_guid_list'] = [safe_guid]  # Trim to essentials
```

### .flow Canvas Size Limits

VNE editor cannot render very large flow graphs. Observed limits:
- **≤21 nodes**: Opens fine ✓
- **~50 nodes**: TBD (test with compact layout)  
- **~80 nodes**: TBD
- **127 nodes**: Black screen or no render

**Layout rules**:
- Keep Y-span under 2000px, X-span under 3000px
- Stack branches horizontally (side-by-side), not vertically
- Use tight spacing: DY=48 for dialog chain, DX=240 between sections
- Prefer `.vns` text script format for complex stories — it compiles to flow internally without needing the visual graph

## Implementation Notes

- Server reads `.vne` file (UTF-8 with BOM, JSON) to get asset registry
- Locates project root by walking up from given path looking for `project.vne`
- All file paths use forward slashes internally, normalized from backslashes
- Search scans `application/` recursively, ignoring binary/unreadable files
- `vne_pack_resources` spawns `python tools/vne-packager/vpak.py pack ...` as subprocess
- `vne_read_vpak` imports the `vpak.py` module directly (sys.path manipulation)
- `vne_console_log` reads `save/diagnostics/mcp_console.jsonl` written by the MCP Console Bridge in `mcp_host.lua`. The bridge wraps LogManager.log() at editor startup and flushes periodically. Log entries use `Engine.JSON.PrintFromLua` for serialization (Lua table → JSON string per line).
