---
name: void-novel-engine
description: VoidNovelEngine (VNE) development — Lua-based visual novel engine on Raylib+SDL. Covers project structure, VPak resource packaging, MCP server for AI interaction, common patterns, and pitfalls.
category: software-development
triggers:
  - Working on VoidNovelEngine code or tools
  - Adding features to the VNE engine (Lua or tooling)
  - VPak resource packaging or loading
  - VNE MCP server usage or extension
  - Debugging VNE export pipeline issues
  - F5 / run / debug not working in VNE editor
  - Finding exported VNE game files
  - Creating VNE game content / visual novel scripts
  - Writing or editing VNS text script files (.vns)
  - Adding new flows, scenes, or resources to a VNE project
  - Generating .flow JSON files programmatically
  - VNE editor crashes when opening .flow files
  - VNE MCP tool development or GitHub push for vne-mcp-server
---

# VoidNovelEngine Development

VoidNovelEngine is a Lua-based visual novel engine running on a C++ core (Raylib + SDL2 + ImGui). Windows-only. The editor is a full IDE with flow-graph designer, text script editor, UI designer, and export pipeline.

## Architecture

```
Engine (C++ native, RaycastEngine.exe)
  └── Engine.SDL    — SDL2 bindings (window, renderer, audio, input, events)
  └── Engine.Raylib — Raylib bindings (textures, audio streaming, shaders)
  └── Engine.ImGUI  — Dear ImGui bindings (editor UI)
  └── Engine.Util   — File I/O, process spawning, string hashing, buffers
  └── Engine.JSON   — JSON parse/serialize

Lua application layer:
  main.lua → application.lua (init)
    └── application/framework/  — Core modules
    └── application/node/       — Flow node definitions
    └── application/pin/        — Pin type definitions
    └── application/scene/      — Scenes (editor, released, etc.)
    └── application/resources/  — Game assets
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `global_context` | Global mutable state (renderer, fonts, window, VPak loader) |
| `resource_index` | Asset registry — scans .meta files, builds GUID index |
| `resources_manager` | Runtime resource loading/caching (texture, audio, font, shader) |
| `flow_manager` | Flow graph / text script document management |
| `settings_manager` | Project settings loaded from `project.vne` (JSON) |
| `native_io` | File system operations — `read_bytes`, `write_text`, `copy_directory`, etc. |
| `native_io_router` | VPak-aware wrapper that intercepts `read_bytes`/`file_exists` |
| `scene_manager` | Scene lifecycle (switch, push, pop) |

### Resource Types

`.png .jpg .webp .tif .avif` → texture
`.wav .mp3 .ogg .flac` → audio
`.mp4 .avi .mkv .webm` → video
`.ttf .otf` → font
`.fs .glsl` → shader
`.flow .vns` → flow script
`.style` → style sheet
`.ui` → UI layout
`.meta` → resource metadata (NOT packaged)

## VNS Text Script Syntax

VNS (`.vns`) is the text-script format for VNE. It compiles to the same node/link graph as `.flow` files but is human-writable. The editor's text script window shows syntax-highlighted VNS with inline preview.

### Structure

```
@@outline("大纲标题")          ← required: sets outline label
@@alias(short = node_type)     ← optional: create shortcuts

#标签名                        ← labels (sections), referenced by @jump and @choice

; 注释                        ← line comments start with ;
```

### Nodes (directives)

All nodes use `@node_name(params)` syntax. Resource references use `&type("name")`.

| Directive | Purpose | Key params |
|-----------|---------|------------|
| `@set_style(&style("path"))` | Load style sheet | — |
| `@clear_style()` | Unload style | — |
| `@bg(&texture("name"), fade_time, wait)` | Switch background | fade_time, wait (bool) |
| `@bgm(&audio("name"), loop, volume, fade_time)` | Play BGM | → token:$var for later stop |
| `@sfx(&audio("name"), loop, volume, fade_time)` | Play SFX | — |
| `@stop_all(fade_time)` | Stop all audio | fade_time |
| `@say("role", "dialogue", wait)` | Show dialog box | role ("" for narration), wait (bool) |
| `@fg(&texture("name"), scale, position, fade_time, wait)` | Add foreground sprite | → foreground:$var |
| `@move($sprite, (x, y), duration, wait)` | Move a foreground | — |
| `@remove($sprite, fade_time, wait)` | Remove foreground | — |
| `@delay(seconds)` | Pause execution | — |
| `@jump(#label)` | Unconditional jump | — |
| `@scene("flow/name.flow")` | Switch to another flow | — |

### Output capture

Use `-> type:$var_name` to capture a node's output into a variable:
```
@bgm(&audio("bgm"), loop: true) -> token:$music
@fg(&texture("girl_1"), scale: 0.9) -> foreground:$heroine
```
Later: `@if($heroine != null) @remove($heroine) @end`

### Choices

```
@choice()
    - "选项文本" -> #标签名
    - "另一个选项" -> #另一个标签
@end
```

All branches must converge or end with `@scene()`.

### Conditionals

```
@if($variable != null)
    @remove($variable, 0.3, wait: false)
@end
```

### Position coordinates

Screen is 1920×1080 by default. Foreground position `(x, y)` is top-left origin. Typical center placement: `(340, 45)` for a character sprite at ~0.88–0.92 scale.

### Resource references

Resources are referenced by their short name (without extension, without path):
```
&texture("study")          → resolves to texture/study.png
&audio("bgm")              → resolves to audio/bgm.wav
&style("style/main.style") → resolves to style/main.style
```

### Pitfalls

- **No `#start` label needed**: The first directive executes immediately. Avoid adding `#start` — it clutters the outline.
- **`wait: true` is the default for `@say`**: Dialog pauses for click. Set `wait: false` only for auto-advancing narration.
- **Foreground removal before scene switch**: Always `@remove()` sprites and `@stop_all()` before `@scene()` or `@clear_style()`. Otherwise sprites may persist visually.
- **Variable scope**: Variables captured with `->` are scoped to the current flow execution. They don't persist across `@scene()` switches.
- **`@scene()` is terminal**: The flow stops executing after `@scene()`. Place it last.

### Example: minimal scene

```
@@outline("示例")
@@alias(bg = switch_background)
@@alias(say = show_dialog_box)
@@alias(scene = switch_scene)

@set_style(&style("style/main.style"))
@bg(&texture("study"), fade_time: 0.5, wait: false)
@delay(0.5)
@say("", "这是一个最简单的场景。", wait: true)
@scene("flow/主菜单.flow")
```

## Debug / F5 Run

Pressing F5 in the editor runs the current flow document in a preview window ("从当前流程调试"). The full call chain:

```
F5 → scene_editor.lua:670 → _run_debug()
  → _get_debug_focus_document()
    → if is_debug_game: return nil
    → if is_flow_designer_window_focused:
        → FlowManager.get_workspace_current_document("graph")
        → fallback: GlobalContext.current_blueprint
    → if story_designer focused:
        → window_story_designer.get_current_document()
    → else: return nil
  → save_manager.begin_new_session()
  → FlowRuntimeHost.execute(document)
```

### Window Focus Requirement

`is_flow_designer_window_focused` is set per-frame in `window_flow_designer.lua:182-184`:
```lua
GlobalContext.is_flow_designer_window_focused = false
local is_window_visible = imgui.Begin("流程脚本视图")
    GlobalContext.is_flow_designer_window_focused = imgui.IsWindowFocused(imgui.FocusedFlags.RootAndChildWindows)
```

The flow designer window ("流程脚本视图") must have ImGui focus. If the user clicks the console, assets panel, settings, or any other docked window, `is_flow_designer_window_focused` becomes `false`.

For text scripts, `window_story_designer.is_window_focused()` is checked instead.

### Pitfall: Silent Failure

**`_run_debug()` returns silently when `_get_debug_focus_document()` returns nil.** No console message, no error, no visual feedback. The user presses F5 and nothing happens.

Diagnosis: check the menu bar "调试 → 从当前流程调试 F5". If grayed out, `_can_run_debug_from_focus()` returned false — no valid document has focus. Click the flow graph editor or text editor to give it focus, then try F5 again.

If the menu item is NOT grayed out but F5 still does nothing, check:
- `resource_modal_active` — a modal dialog may be blocking shortcuts
- `EditorPreviewInput.should_block_editor_shortcuts()` — returns true when in debug mode with preview focused
- `GlobalContext.is_debug_game` — may be stuck true from a previous crashed session (requires editor restart to clear)

Also note: `_run_debug()` is gated behind `if not resource_modal_active and not block_editor_shortcuts then` in `scene_editor.lua:657`. Any active resource modal or preview focus blocks ALL keyboard shortcuts including F5.

## VPak Resource Packaging

### Format (little-endian binary)

```
[4] Magic "VPAK"
[4] Version uint32 (=1)
[4] Flags uint32 (bit0=encrypted, bit1=compressed)
[4] File count uint32
[N×32] File table entries:
  [8] Name hash uint64 (SHA256(path)[:8] → struct.unpack '<Q')
  [8] Data offset uint64
  [8] Packed size uint64
  [8] Original size uint64
[N] Data section
```

### Encryption

XOR cipher with 256-byte rotating key derived from seed string via SHA256 + deterministic scrambling (`h[i] ^ ((i * 0x9D) & 0xFF)`). Match key derivation between Python and Lua implementations.

### Files

| File | Role |
|------|------|
| `tools/vne-packager/vpak.py` | Python CLI: pack, list, extract. **Primary packer for export.** |
| `application/framework/vpak_loader.lua` | Runtime: open archives, index by hash, read/decode files |
| `application/framework/vpak_pack_step.lua` | Lua packer — **deprecated for export**, kept for reference. Has userdata path issues (see pitfalls). |
| `application/framework/native_io_router.lua` | Transparent VPak interceptor for NativeIO.read_bytes |

### Workflow

1. Export pipeline copies `application/resources/` to release dir (`.temp/` for single-file)
2. **Python packager** (`tools/vne-packager/vpak.py`) runs as subprocess: SHA256-hashes paths, XOR-encrypts files, builds `resources.vpak`
3. Deletes loose resource files, keeps .meta for resource index
4. Enigma Virtual Box packs everything into single `.exe` (if `single_file: true`)
5. At runtime, `application.lua` detects `resources.vpak`, initializes VPakLoader
6. `NativeIORouter` intercepts `read_bytes` calls → routes through VPak first, falls back to disk

The VPak call in `window_exporter.lua` has been replaced with a Python subprocess call. It auto-discovers Python via PATH (`python`/`python3`/`py`) plus known install paths (`D:\\AI\\python312\\python.exe`, `C:\\Python312\\python.exe`). Key `VNE_VPAK_DEFAULT_KEY_2024`, no compression (`--no-compress`).

### Pitfalls

- **MCP asset registry caching**: The VNE MCP server loads the asset registry (`project.vne`) at startup and caches it. Files created via the filesystem (write_file/terminal) while the MCP server is running will NOT appear in `vne_list_resources` or `vne_get_resource` until the VNE editor (and thus its MCP server subprocess) is restarted. The files ARE on disk and correctly registered in `project.vne` — the issue is purely the MCP server's in-memory cache. To verify files were created correctly, read `project.vne` directly with `terminal` + Python, or use `vne_read_file` (which reads from disk, not cache).
- **CRITICAL: VNE NativeIO paths are userdata, not Lua strings.** `NativeIO.list_directory_array` returns paths as userdata objects. `string.byte`, `string.sub`, and `tostring()` all fail on them in VNE's Lua environment. This blocks any pure-Lua packer from hashing paths. **The export pipeline avoids this by calling the Python packager as a subprocess.** The Lua packer (`vpak_pack_step.lua`) is effectively deprecated — do not try to fix or use it for export.
- **Runtime loader still uses FNV-1a hash**: `vpak_loader.lua` needs a working hash function for runtime VPak lookups. Its `_hash_string` uses FNV-1a with `string.format("%s", s)` conversion. The loader encounters paths from VPak metadata (strings), not from `list_directory_array` (userdata), so the userdata issue doesn't apply at runtime.
- **`util.HashString` does NOT exist**: `Engine.Util` in VNE does not expose a `HashString` function. Both `vpak_pack_step.lua` and `vpak_loader.lua` originally called `util.HashString(relative_path)` which is nil.
- **Pure-Lua packer has no compression**: `vpak_pack_step.lua` cannot do zlib compression. Python packager supports `--compress` flag.
- **VPak init must happen before resource loading**: `application.lua` inits VPakLoader right after window/icon setup, before any `ResourcesManager` calls.
- **.meta files stay on disk**: Resource index needs them. Only asset binary files go into VPak.
- **VPak errors are caught silently**: The `on_export_windows()` wraps VPak in `pcall`. If VPak fails, the warning is logged but export continues with loose files. Check console for "资源打包失败" or "资源打包完成（Python packager）".
- **Both packer and loader need identical `_hash_string`**: If modifying the hash function, patch BOTH `vpak_pack_step.lua` and `vpak_loader.lua`.
- **Python discovery in exporter**: PATH search (`python`/`python3`/`py`) then known paths (`D:\\AI\\python312\\python.exe`, `C:\\Python312\\python.exe`). If Python install location changes, update the known-paths list in `window_exporter.lua`.

### FNV-1a Hash Implementation (for vpak_loader.lua)

The runtime loader needs a working replacement for `util.HashString`. Place this after `_xor_crypt` and before `_xxh64_style_hash`:

```lua
local function _hash_string(s)
    -- FNV-1a 32-bit hash (pure Lua, no engine dependency)
    -- VNE paths may be userdata; force string conversion
    s = string.format("%s", s)
    local hash = 2166136261  -- offset basis
    for i = 1, #s do
        hash = hash ~ string.byte(s, i)
        hash = (hash * 16777619) % 4294967296  -- prime, mod 2^32
    end
    return hash
end
```

Then replace all `util.HashString(relative_path)` calls with `_hash_string(relative_path)` in `VPakLoader.path_hash()` and `_xxh64_style_hash()`.

The packer (`vpak_pack_step.lua`) has the same function for consistency, but it's not used in the export pipeline — the Python packager handles all VPak creation.

## VNE MCP Server

**Canonical distribution:** standalone repo at `https://github.com/zv163/vne-mcp-server` (public). The in-project copy at `tools/vne-mcp-server/vne_mcp_server.py` is the original; the standalone repo (`/home/zv/workspace/vne-mcp-server/`) is the canonical source for external distribution. For development work, patch the standalone repo first, then sync back to the VNE project tree. Both copies must keep `vpak.py` in the same directory.

Server version: **1.3.0**. Zero external dependencies — uses only Python stdlib.

### Protocol

Stdio JSON-RPC 2.0, protocol version `2025-11-25` (latest stable). Server reads one JSON object per line from stdin, writes one per line to stdout. The `instructions` field in the initialize response provides a hint to LLM clients about how to use the 16 tools.

### 16 Tools

| Tool | Purpose | Since |
|------|---------|-------|
| `vne_project_info` | Project version, asset counts by type, paths | 1.0 |
| `vne_list_resources` | Filter by type (texture, audio, flow, etc.) | 1.0 |
| `vne_read_file` | Read any project file by relative path | 1.0 |
| `vne_list_directory` | List directory contents | 1.0 |
| `vne_search` | Case-insensitive text search in Lua files | 1.0 |
| `vne_get_resource` | Resource detail by GUID (includes .meta) | 1.0 |
| `vne_lua_api` | Engine module reference, project structure, resource types | 1.0 |
| `vne_export_config` | Export settings from project.vne, VPak status | 1.0 |
| `vne_pack_resources` | Invoke Python packager for VPak creation | 1.0 |
| `vne_read_vpak` | List or extract files from VPak archives | 1.0 |
| `vne_console_log` | Read real-time editor console output | 1.1 |
| `vne_refresh_assets` | Clear cache, re-read project.vne (no restart needed) | 1.2 |
| `vne_register_asset` | Atomically create .meta + register in project.vne | 1.2 |
| `vne_validate_flow` | Validate .flow files for pin key errors before opening | 1.2 |
| `vne_list_node_types` | List all flow node type_ids with pin schemas | 1.2 |
| `vne_reload_custom_nodes` | Hot-reload custom node definitions without restarting VNE | **1.3** |

Full API reference: `references/mcp-api.md`.

### New in v1.3.0 — hot-reload custom nodes

- **`vne_reload_custom_nodes`**: Writes a trigger flag file (`save/temp/_reload_custom_nodes.flag`) that `mcp_host.lua` detects each frame. On detection, calls `definition_loader.load()` to reload all node/pin definitions, then writes a result file. **Eliminates the need to restart VNE after editing custom node .lua files.** Requires one-time VNE restart to activate the mcp_host.lua watcher. See `vne-custom-extensions` skill → Hot-Reload section for architecture details.

### New in v1.2.0 — 4 tools for safer flow creation

These tools were added based on real-world pain points discovered while building a campus romance VN:

- **`vne_refresh_assets`**: Clears the MCP server's internal cache and forces re-reading project.vne. Call after creating files externally. **Eliminates the need to restart VNE editor.**
- **`vne_register_asset`**: Creates the .meta file AND updates project.vne atomically. One call instead of manual JSON editing.
- **`vne_validate_flow`**: Checks .flow JSON for wrong pin keys (e.g. `route_1` vs `choice_1`), missing merge_flow keys, broken links, missing shader pins, wrong psv versions. **Always call before opening a generated .flow in VNE.**
- **`vne_list_node_types`**: Discovers 70+ node types with full pin schemas. **Use before generating .flow to avoid wrong pin keys.**

## Dialog System

`show_dialog_box` does NOT auto-replace previous text. Each call creates a separate Billboard.
**For chained dialogue, use `show_subtitle`** (auto-replaces). Prefix names: `【张晨】对话`.
**For show_dialog_box, always pair with hide_dialog_box** connected BOTH via flow AND dialog_box object pin.
`hide_dialog_box` params: `fade_out_time=0.05, wait_interaction=false` (user-specified optimal value).

## Flow Graph Z-Order

Blueprint patch adds "提到最前 / 放回原位" to node right-click menu. See `references/blueprint-zorder-patch.md`.

## Flow generation: use vne-flow-patterns skill

When generating .flow files programmatically, load `vne-flow-patterns` first.
See `references/dialog-patterns.md` for the `DialogChain` helper and scene templates.
Key rules: split at background changes, always pass `in_flow` to DialogChain, hide_dialog_box needs object link.

### Configuration for MCP Clients

**Generic MCP client** (Claude Desktop, Cursor, etc.):
```json
{
  "mcpServers": {
    "vne": {
      "command": "python",
      "args": ["tools/vne-mcp-server/vne_mcp_server.py", "--project-path", "/path/to/VoidNovelEngine"]
    }
  }
}
```

**Hermes Agent** — requires a wrapper script because `hermes mcp add --args` cannot pass `--project-path` (argparse tries to parse it as a hermes flag):

```bash
# Create wrapper
cat > ~/.hermes/scripts/vne-mcp-wrapper.sh << 'EOF'
#!/bin/bash
exec python3 /mnt/d/A-Game/VoidNovelEngine/tools/vne-mcp-server/vne_mcp_server.py \
  --project-path /mnt/d/A-Game/VoidNovelEngine "$@"
EOF
chmod +x ~/.hermes/scripts/vne-mcp-wrapper.sh

# Add to Hermes
echo "y" | hermes mcp add vne --command ~/.hermes/scripts/vne-mcp-wrapper.sh
```

After config update, MCP tools are only available in new sessions (no hot-reload).

### Standalone Distribution

The MCP server + VPak packager are published as a standalone open-source repo:

| Item | Value |
|------|-------|
| Local path | `/home/zv/workspace/vne-mcp-server/` |
| GitHub URL | `https://github.com/zv163/vne-mcp-server` (public) |
| Contents | `vne_mcp_server.py`, `vpak.py`, 3× README (CN/EN/JP), `LICENSE` (MIT) |

The READMEs use a **multi-language badge-switching pattern** modeled after Hermes Agent — each file has `[中文] [English] [日本語]` shield badges at the top that link to the other language versions:
- `README.md` — Chinese (default, primary)
- `README.en.md` — English
- `README.ja.md` — Japanese

Each README covers: quick-start commands, 11-tool feature table with R/O column, 4 MCP client config examples (Claude Desktop / Cursor / Hermes / generic), stdio vs TCP/HTTP transport, VNE editor integration with ASCII architecture diagram, and standalone VPak CLI usage.

**Convention: when creating documentation for VNE-related tools or projects, default to Chinese as the primary language with `.en.md` and `.ja.md` alternates.** Use the badge-switching pattern from this repo — it's the user's preferred format.

The repo is a self-contained copy — no filesystem dependency on the VNE project tree. Clone it once and point `--project-path` at any VNE project. To update it, edit files under `/home/zv/workspace/vne-mcp-server/` and push to `zv163/vne-mcp-server` on GitHub.

### Pitfalls

- Server uses `os.getcwd()` when no `--project-path` given — make sure the client launches it from the VNE project root
- `vne_pack_resources` calls the Python packager as a subprocess — needs `vpak.py` at `tools/vne-packager/vpak.py`
- Resource paths in the asset registry are Windows-style backslash paths — normalize when comparing
- **`vne_console_log` returns `no_log_file`**: VNE editor must be running with the Console Bridge active. Restart VNE after updating `mcp_host.lua`. The bridge writes to `save/diagnostics/mcp_console.jsonl`.
- **`vne_export_config` shows `has_vpak: false`**: This reads the editor's `project.vne` (where `release_mode` is false). The exported game's `project.vne` has `release_mode: true` and likely had VPak enabled during export (`vpak_enabled` defaults to true). Do not rely on this field to determine whether the exported build uses VPak — check the release directory directly.
- **MCP server caches asset registry at startup**: `vne_list_resources` and `vne_get_resource` read from the in-memory asset registry loaded when the MCP server starts. New resources added to disk (new .vns + .meta files, updated project.vne) will NOT appear in these tools until the MCP connection is restarted. The filesystem tools (`vne_read_file`, `vne_list_directory`) will see new files immediately — use those to verify file creation. To make new resources visible in the asset registry, restart the VNE editor or the MCP server connection.

## Creating Flows Programmatically (via MCP / Filesystem)

Preferred v1.2.0 workflow (use MCP tools):

1. `vne_list_node_types` — see available nodes and correct pin keys
2. Generate .flow JSON (use `scripts/gen_flow_template.py` as starting point)
3. `vne_validate_flow` — catch pin key errors BEFORE opening in editor
4. `vne_register_asset` — one call creates .meta + registers in project.vne
5. `vne_refresh_assets` — clear MCP cache so new asset is visible

Legacy manual workflow (if MCP tools unavailable):

1. **Generate a GUID**: `python3 -c "import uuid; print(str(uuid.uuid4()))"`
2. **Write the .vns script**: Create `application/resources/flow/<name>.vns` (see VNS Text Script Syntax above)
3. **Create the .meta file**: Write `application/resources/flow/<name>.vns.meta` with `{"version":1,"importer":[],"guid":"<GUID>"}`
4. **Get file stats**: `stat --format='%Y %s'` for mtime and size
5. **Register in project.vne**: Add asset entry to `asset_registry.assets` + prepend GUID to `open_flow_guid_list`
6. **Restart VNE editor** to pick up new resource

### project.vne quirks

- The file may be **minified** (single-line JSON). Use Python `json.load()` + `json.dump()` for safe modification.
- JSON uses `separators=(',', ':')` for minified format.
- The `open_flow_guid_list` array controls which flows appear in the editor's tabs.

### Verification

- `vne_read_file` with the path — confirms content
- `vne_list_directory` on `application/resources/flow/` — confirms files exist
- `vne_refresh_assets` then `vne_list_resources` — confirms registry updated
- Terminal `ls -la` — confirms file sizes

## Flow Graph (.flow) Generation

See `references/flow-generation.md` for complete node schemas and crash-prevention rules.

### Critical crash-causing mistakes (ALWAYS check with vne_validate_flow)

| Node | Wrong | Correct | Severity |
|------|-------|---------|----------|
| `show_choice_button` outputs | `route_1`, `route_2`, `route_3` | `choice_1`, `choice_2`, `choice_3` | **CRASH** |
| `merge_flow` inputs | (missing key) | Requires `"key": "in_1"` etc | **CRASH** |
| `switch_background` psv | `pin_schema_version: 1` | `pin_schema_version: 2` | Warning |
| Foreground pins | Not connected | Link `add_foreground.foreground` → `remove_foreground.foreground` | Runtime fail |

### Canvas size limits

VNE flow designer has a **hard limit of 80 nodes per .flow file**. Exceeding this causes:
- 82+ nodes: editor may freeze or crash on open
- 127+ nodes / 5500px Y-span: black screen (viewport lost)

Node counts from testing:
- 3–21 nodes: Safe ✓
- 52 nodes: Safe ✓  
- 82 nodes: Borderline — may work or may crash
- 127 nodes: Broken ✗ (black screen)

**Rule: never exceed 80 nodes per .flow file.** For stories that require more nodes, split into multiple scenes connected via `switch_scene`.

### Scene splitting pattern

When a story exceeds 80 nodes, split into separate .flow files:

```
Scene 1 (entry): 教室→对话→选择
    ↓ choice_1         ↓ choice_2         ↓ choice_3
Scene 2: 分支+结局    Scene 3: 分支+结局    Scene 4: 分支+结局
    ↓                   ↓                   ↓
  主菜单              主菜单              主菜单
```

Each branch scene is its own .flow file with its own `entry`→`set_style`→dialogues→`stop_all_audio`→`clear_style`→`switch_scene("flow/主菜单.flow")`.

Scene 1's choice outputs connect to `switch_scene` nodes that jump to each branch scene:
```python
cho,chi=N('show_choice_button',...,[('choice_1','flow'),('choice_2','flow'),('choice_3','flow')],...)
sco,sci=N('switch_scene',[('in','flow'),('target','string','flow/校园恋爱_勇敢.flow')],[],...)
L(cho['choice_1'],sci['in'])
```

Each scene stays under 80 nodes (typically 25–50 nodes each).

Layout rules:
- Stack branches HORIZONTALLY (side-by-side) not vertically
- Use DY=48 for dialog spacing, DX=240 for column spacing
- Keep Y-span under 2000px, X-span under 3000px

### Template script

`scripts/gen_flow_template.py` — minimal skeleton to copy and extend. Includes helper functions for node creation, linking, and chaining.

### For complex stories

Prefer `.vns` text script format over `.flow` for stories with many dialogue lines. VNS compiles to the same internal graph but doesn't need the visual editor. Reserve `.flow` for demos under 30 nodes.

## MCP Console Log Bridge

The `mcp_host.lua` module hosts a **Console Log Bridge** that captures all LogManager output to a file so AI assistants can read the VNE editor console in near-real-time.

### How it works

1. At editor startup, `MCPHost.init()` calls `_console_log_init()`
2. `_console_log_init()` wraps `LogManager.log()` — every log call (info, warning, error, success, debug) is intercepted
3. Entries are serialized to JSON via `Engine.JSON.PrintFromLua` and written to `save/diagnostics/mcp_console.jsonl`
4. Ring buffer of 500 entries max, flushed to disk every 1 second
5. On shutdown, the original `LogManager.log` is restored

### Python Discovery in mcp_host.lua

`_find_python()` searches for Python on Windows to launch the MCP TCP server. Search order:

1. **PATH commands**: `python.exe`, `python3.exe`, `py.exe`, `python`, `python3`
2. **Common install dirs** on C: and D: (versions 3.7–3.13):
   - `%LOCALAPPDATA%\Programs\Python\Python3xx\`
   - `%ProgramFiles%\Python3xx\`
   - `D:\AI\python3xx\`, `D:\Python3xx\`
3. **Windows Store**: `%LOCALAPPDATA%\Microsoft\WindowsApps\`
4. **WSL**: `wsl python3`

Key: On Windows, `CreateProcess` needs `.exe` extension — always try `python.exe` before bare `python`.

### Redundant file

`mcp_runtime.lua` was an early standalone attempt at the console bridge. Its functionality has been merged into `mcp_host.lua`. The file can be deleted.

## Export Pipeline

Controlled by `application/scene/window/window_exporter.lua`. The export panel is under the "发布设置" window.

### Entry Flow

`entry_flow_guid` in `project.vne` specifies the entry flow for release builds. If empty, `_resolve_release_entry_flow_guid()` applies fallbacks in order:
1. Current flow (`current_flow_guid`)
2. Current graph flow (`current_graph_flow_guid`)  
3. Current text flow (`current_text_flow_guid`)
4. Any open flow from `open_flow_guid_list`

If all fallbacks fail, export aborts with "发布入口流程未设置".

### Build Steps (Windows)

All logic in `on_export_windows()`:

1. **Save all open documents** — flows, styles, UIs
2. **Build release directory** — `release/Windows/` (cleared first)
3. **Single-file mode** — copies to `release/Windows/.temp/` instead
4. **Copy essential files** — `application/`, `main.lua`, `RaycastEngine.exe`
5. **Video transcode check** — ensures video artifacts are ready
6. **Generate definition manifest** — `application/definition_manifest.json`
7. **Generate plugin manifest** — `application/plugin_manifest.json`
8. **VPak resource packaging** — Python packager (`tools/vne-packager/vpak.py`) run as subprocess (XOR encryption, `--no-compress`). Uses `VNE_VPAK_DEFAULT_KEY_2024`. The deprecated Lua packer (`vpak_pack_step.lua`) has userdata path issues and is NOT used.
9. **Compile Lua scripts** — `luac54.exe` compiles all `.lua` to bytecode
10. **Write release project.vne** — sets `release_mode: true`
11. **Rename exe** → `VoidNovelEngineGame.exe`
12. **rcedit metadata** — icon, version, developer, description
13. **EnigmaVB single-file** (if `single_file: true`) — PowerShell script packs everything into one `.exe`

### Output

| Mode | Path | Notes |
|------|------|-------|
| Single-file | `release/Windows/VoidNovelEngineGame.exe` | One .exe, includes all assets |
| Multi-file | `release/Windows/` | Full directory with exe + assets |

### VPak in Export

`vpak_enabled` defaults to `true`. The export calls the **Python packager** (`tools/vne-packager/vpak.py`) as a subprocess via `NativeIO.run_process_capture`. Uses `--key VNE_VPAK_DEFAULT_KEY_2024 --no-compress`. On failure, the pcall catches the error and logs a warning — export continues with loose files.

Python auto-discovery: tries `python`, `python3`, `py` via `--version` check, then falls back to known paths (`D:\\AI\\python312\\python.exe`, `D:\\AI\\python311\\python.exe`, `C:\\Python312\\python.exe`). If none found, logs "未找到 Python" and skips VPak.

## Flow Graph Format (.flow)

The `.flow` file is the JSON-serialized node graph used by VNE's visual flow designer (流程脚本视图). Full format spec: `references/flow-format.md`.

Programmatic generation helper: `scripts/gen_flow.py` — Python `FlowBuilder` class with chainable node builders (entry, set_style, switch_background, dialog, add_foreground, choice, merge_flow, etc.). Import it to generate .flow JSON without hand-writing pin IDs.

Key points when generating .flow:
- All node/pin/link IDs share one global ID space (`max_uid`)
- `pin_schema_version` is always 1
- Dialog nodes only need `role_text`, `dialogue_text`, `wait_interaction` — omit style pins (fonts, colors, etc.) to inherit from `set_style`
- `show_choice_button` has NO general `out` pin — only `route_1/2/3`
- `switch_scene` has NO outputs (terminal node)
- `merge_flow` joins 3 flow inputs into 1 output (use after choice branches)
- Resource references: `{"guid": "...", "path_hint": "texture/foo.png"}` on input pins

## Project Conventions

- Working directory: `/mnt/d/A-Game/VoidNovelEngine` (WSL path for Windows D: drive)
- Engine exe: `RaycastEngine.exe` (in project root, referenced via `util.GetExeFilePath()`)
- Project config: `project.vne` (JSON, UTF-8 with BOM)
- Export output: `release/Windows/VoidNovelEngineGame.exe` (single-file) or `release/Windows/` (multi-file)
- External tools: `application/external/` (luac54.exe, rcedit.exe, ffmpeg.exe, ImageMagick, EnigmaVirtualBox)
- All Lua files use tabs for indentation (matching existing codebase)
- Chinese comments and log messages are used throughout (the engine UI is Chinese)
- **Multi-language docs**: default to Chinese as primary language with `.en.md` and `.ja.md` alternates. Use Hermes Agent-style badge switching (`[中文] [English] [日本語]` shield badges at top) linking to the other language files. This is the user's preferred documentation format for all VNE-related tools.
- **MCP protocol**: always use the latest stable MCP protocol version. As of 2026-06-13 that is `2025-11-25`. Check the MCP spec repo (`modelcontextprotocol/specification`) for newer versions and upgrade proactively — the user expects currency, not compatibility-minimum.

## .flow Generation Rules

When generating .flow files programmatically, see `references/mcp-api.md` for the full pitfall table. Key rules:

1. **Validate before opening**: generate .flow → `vne_validate_flow` → fix errors → register → `vne_refresh_assets` → open in editor
2. **Pin keys are exact**: `show_choice_button` outputs are `choice_1` through `choice_5`, NOT `route_1`
3. **Pin IDs are integers**: links must use int pin IDs. A common bug is passing `N()`'s return dicts (e.g. `{'in': 177}`) instead of extracting `dict['in']` (int `177`) — this causes immediate crash
4. **merge_flow inputs need keys**: the node definition doesn't auto-assign keys to its input pins
5. **switch_background** needs `pin_schema_version: 2`
6. **Foreground connections**: `add_foreground`'s `foreground` output pin must be linked to `remove_foreground`/`move_foreground`'s `foreground` input pin
7. **Node count limit**: Hard limit is **80 nodes per .flow file**. ≤52 confirmed safe, 82 borderline, 127 broken (black screen). For stories requiring more, split into multiple scenes connected via `switch_scene` (see Scene Splitting Pattern above).
8. **dict-in-link bug**: passing `N()` return dicts directly to `L()` (e.g. `L(f, di)` where `di={'in':177}`) instead of extracting pin IDs (`L(f, di['in'])`) causes immediate crash. `vne_validate_flow` v1.2.1+ catches this.
9. **Layout**: Y-span under 2000px, X-span under 3000px. Branches side-by-side, not stacked vertically. DY=48, DX=240.
10. **Startup crash**: if VNE crashes on launch, check `current_graph_flow_guid` in project.vne — it may point to a large flow. Reset to a safe GUID.

## VNE Editor Startup Crash Recovery

If VNE crashes on startup, reset `current_graph_flow_guid` and `current_flow_guid` in project.vne to a known-working flow (e.g. 主菜单.flow), and trim `open_flow_guid_list`. The editor restores previous session state on launch; pointing at a large/broken flow causes immediate crash with no visible error.

## Reference Files

- `references/vpak-spec.md` — Complete VPak binary format specification
- `references/mcp-api.md` — Full VNE MCP server API reference (16 tools, v1.3.0)
- `references/flow-generation.md` — .flow JSON format guide: node schemas, pin keys, crash pitfalls, canvas limits
- `scripts/gen_flow_template.py` — Minimal .flow generator skeleton to copy and extend

## 🔟 十大陷阱 (Top 10 Pitfalls)

在校园恋爱视觉小说项目中反复验证的引擎陷阱，每次生成 .flow 前必须检查。

| # | 陷阱 | 症状 | 正确做法 |
|---|------|------|---------|
| 1 | `show_choice_button` 输出 key = `route_1` | 点击后崩溃/无响应 | 用 `choice_1`~`choice_5`，不是 `route_1` |
| 2 | `add_foreground` 缺 `shader` pin | 前景图不显示 | `pin_schema_version`=2，必须含 7 个输入 pin（含 shader） |
| 3 | `merge_flow` 输入 pin 缺 key | 编辑器崩溃 | 避免使用此节点；用 `switch_scene` 拆分场景代替合并 |
| 4 | 单 .flow 超 80 节点 | 编辑器卡死/黑屏 | 拆分为多场景（≤60 节点安全），用 `switch_scene` 连接 |
| 5 | `show_dialog_box` 不会自动替换 | 旧对话框不消失 | 每个 show 后跟 `hide_dialog_box`（fade=0.05），通过 `dialog_box` object pin 链接 |
| 6 | 对话框隐藏无链接 | 对话框残留 | `hide(fade=0.05)` + 下一个 `show_dialog_box` 必须通过 `dialog_box` 引脚连接 |
| 7 | 同场景换背景 | 节点暴涨 | 换背景 = 开新场景 `switch_scene`，每场景 < 60 节点 |
| 8 | 分支选择后 pin key 不匹配 | 点击后无反应 | `show_choice_button` 输出 key 是 `choice_1`，`choice_2`...不是 `branch_1` |
| 9 | link 的 `pin_id` 是 string | 编辑器直接崩溃 | `pin_id` 必须是 int（JSON number），不能是字符串 "1" |
| 10 | 启动崩溃（无报错） | VNE 打不开 | 删除 `project.vne` 中 `current_graph_flow_guid`（指向大文件导致） |

**dialog_line 节点陷阱**（v1.3.0）:
- 所有可选引脚（`prev_dialog`、`audio`）必须用 `try_check_input` 而非 `check_input`
- 字体不能传工厂函数，必须用 `GlobalContext.font_wrapper_sdl`
- 音频模块是 `AudioPlaybackManager`，不是 `AudioManager`
- 隐藏上句用 `Billboard:hide(0.05)`，不是 `scene:remove_object()`
