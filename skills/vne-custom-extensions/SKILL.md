---
name: vne-custom-extensions
description: VNE3 custom node, pin, scene, and plugin development — complete reference from official VNEdev3 documentation (12-page CustomExtension guide) and WolfAndStar implementation patterns.
category: software-development
triggers:
  - Creating custom VNE flow nodes
  - Adding new pin types to VNE
  - Building custom scenes (mini-games, battles)
  - Creating VNE plugins with manifest.json
  - Extending VNE with Lua
  - Building terminal/CLI gameplay mechanics
---

# VNE Custom Extensions

From official VNE3 docs (v0.1.0-dev.3, 12-page guide) + WolfAndStar patterns.

## Decision Tree

| Need | Use | Template |
|------|-----|----------|
| One action in flow graph | Custom Node | `application/node/custom/_自定义节点模板.lua` |
| New data type + editor | Custom Pin | `application/pin/custom/_自定义引脚模板.lua` |
| update/render loop | Custom Scene | `application/scene/_自定义场景模板.lua` |
| Packaged feature (auto-register) | Plugin System | `plugins/my_plugin/manifest.json` |

## Custom Nodes

### Node Definition
```lua
local NodeDef = {
    type_id = "my_node",          -- UNIQUE, no duplicates!
    name = "显示名称",
    icon_id = "puzzle-fill",       -- RemixIcon, NOT "icon"
    color = imgui.ImVec4(imgui.ImColor(218, 144, 97, 255).value),
    category = "分类名",
    category_order = 5,
    order = 1,
    menu_visible = true,
    keywords = {"搜索词"},
}
```

### Pin Registration
```lua
builder:add_input({key = "in", type_id = "flow"})
builder:add_input({key = "text", type_id = "string", name = "文本"})
builder:add_output({key = "out", type_id = "flow"})
builder:add_output({key = "result", type_id = "string", name = "结果"})
```

### Runtime Execution
```lua
node.on_execute = function(self, scene)
    local text = NodeRuntimeHelper.check_string(self, "text")
    local num = NodeRuntimeHelper.check_int(self, "count")
    local flag = NodeRuntimeHelper.check_bool(self, "enabled")
    local tex = NodeRuntimeHelper.check_resource(self, "tex_pin", "texture")
    
    NodeRuntimeHelper.set_output(self, "result", processed)
    NodeRuntimeHelper.execute_next_node(self, "out")
end

node.on_execute_update = function(self, scene, delta)
    -- For multi-frame operations (wait for interaction, animation, etc.)
    if ready then
        NodeRuntimeHelper.wait_interact_to_next_node(self, "out")
    end
end
```

### CRITICAL RULES
- Every pin MUST have a stable `key` — used for save/load, .vns commands, plugin bindings
- Custom nodes DO hot-reload via `vne_reload_custom_nodes` MCP tool (v1.3.0+). Edit → call tool → VNE picks up changes in ~1 frame. See Hot-Reload section below.
- Use `icon_id` not `icon` in node defs
- Use `Billboard` API (not show_dialog_box node) when building dialogue custom nodes — it gives full lifecycle control inside a single node. See vne-flow-patterns skill → Pattern D (dialog_line) for a complete worked example with chain-linking via object pins.
- `object_type` on object pins: set `options = {object_type = "dialog_box"}` on both input (prev_dialog) and output (dialog_box) pins so the editor enforces type-safe connections.
- `node._id:get()` is available inside `Common.make_definition` callback — use it like the built-in nodes do (e.g. `local object_id <const> = string.format("dl_%d", node._id:get())`).
- Always set `<const>` on the object_id local so LuaJIT optimizes it.
- **Optional object pins**: use `try_check_input` (returns nil on empty) instead of `check_input` (aborts on empty). The first node in a chain has no previous dialog — `check_input` will crash.

### dialog_line custom node — complete worked example

The most requested custom node: one node that hides the previous dialog box,
optionally plays audio, and shows the next dialog — all in a single flow node.

**Required modules (exact names):**
```lua
local Common = require("application.framework.builtin_node_common")
local AudioPlaybackManager = require("application.framework.audio_playback_manager")  -- NOT AudioManager!
local RuntimeLayout = require("application.framework.runtime_layout_context")
local GlobalContext = require("application.framework.global_context")
```

**Correct Billboard constructor call:**
```lua
local convert_color = NodeRuntimeHelper.convert_imvec4_to_sdl_color  -- NOT raw SDL_Color!
local default_font = GlobalContext.font_wrapper_sdl  -- NOT Common.default_font_reference (factory!)

local dialog_box = Billboard.new(
    role_text,                                      -- name (string)
    dialogue_text,                                  -- dialogue (string)
    140, 760, 1640,                                 -- x, y, width
    default_font, default_font,                     -- role_font, dialogue_font (FontWrapper, not function)
    convert_color(imgui.ImVec4(1, 0.9, 0.65, 1)),  -- role_color → SDL_Color
    convert_color(imgui.ImVec4(0.96, 0.96, 0.96, 1)), -- dialogue_color
    convert_color(imgui.ImVec4(0.06, 0.09, 0.13, 0.86)), -- bg_color
    0.2,                                            -- fade_in time
    nil,                                            -- background image
    RuntimeLayout.scale_font_size(28),              -- role font size
    RuntimeLayout.scale_font_size(25)               -- dialogue font size
)
scene:add_object(dialog_box, object_id, 50)
```

**Hide previous dialog (correct API):**
```lua
-- Use try_check_input — returns nil when pin is empty (first node in chain has no prev)!
-- check_input would ABORT on empty, crashing the flow.
local prev_db = NodeRuntimeHelper.try_check_input(self, "prev_dialog", "object")
if prev_db and type(prev_db) == "table" and prev_db.hide then
    prev_db:hide(0.05)  -- fade-out tween, NOT scene:remove_object()!
end
```

**Play audio (optional — use try_check_input, NOT check_resource!):**
```lua
-- check_resource ABORTS when audio pin is empty. Use try_check_input.
local audio_ref = NodeRuntimeHelper.try_check_input(self, "audio", "audio")
if audio_ref then
    AudioPlaybackManager.play(audio_ref, {  -- NOT AudioManager!
        loop_count = 0,
        volume = vol,
        fade_in_seconds = 0,
    })
end
```

**Wait for interaction (correct pattern):**
```lua
node.on_execute_update = function(self, scene, delta)
    local dialog_box = scene:find_object(object_id)
    if dialog_box and dialog_box._progress == 1 then  -- fade-in complete
        NodeRuntimeHelper.wait_interact_to_next_node(self, "out")
    end
end
```

**Common mistakes when building dialogue nodes:**
| Wrong | Right | Why |
|-------|-------|-----|
| `require("application.framework.audio_manager")` | `require("application.framework.audio_playback_manager")` | AudioManager doesn't exist |
| `scene:remove_object(prev_db)` | `prev_db:hide(0.05)` | No fade animation, jarring cut |
| `Common.default_font_reference` as font arg | `GlobalContext.font_wrapper_sdl` | Factory function, not a font |
| `Common.sdl.SDL_Color(r,g,b,a)` | `NodeRuntimeHelper.convert_imvec4_to_sdl_color(imvec4)` | Inconsistent with built-in |
| `check_input(self, "prev_dialog")` | `try_check_input(self, "prev_dialog", "object")` | check_input ABORTS on nil — first node in chain has no prev! |
| `check_resource(self, "prev_dialog", "object")` | `try_check_input(self, "prev_dialog", "object")` | Object pins need check_input/try_check_input, not check_resource |
| `check_resource(self, "audio", "audio")` | `try_check_input(self, "audio", "audio")` | check_resource ABORTS on nil — same as check_input! Use try_check_input for optional resource pins |
| Skipping type check on prev_db | `type(prev_db) == "table" and prev_db.hide` | Guard against nil/unconnected

### Hot-reload pitfall: reopen flow files after reload
After `definition_loader.load()` updates the registry, **existing node instances in open flow tabs still reference old definitions**. The flow file must be re-opened (close + reopen in editor, or touch the .flow file on disk to trigger auto-reload) for new definitions to take effect on those instances.

## Hot-Reload Custom Nodes (v1.3.0+)

**No more restarting VNE after every edit.** Call `vne_reload_custom_nodes` MCP tool.

### How it works (flag-file architecture)

```
MCP tool writes: save/temp/_reload_custom_nodes.flag
        │
mcp_host.lua (every frame) detects flag
        │  removes flag, calls:
        ▼
definition_loader.load() — reloads ALL node/pin definitions
        │  writes result file:
        ▼
save/temp/_reload_custom_nodes.result → "success" or "error: ..."
        │
MCP tool polls result file, returns to agent
```

### Requirements
- VNE must be running (mcp_host.lua monitors the flag each frame)
- The `mcp_host.lua` with the watcher code must be loaded (restart VNE once after initial install)
- The MCP server must be v1.3.0+ (16 tools, includes `vne_reload_custom_nodes`)

### Usage workflow
1. Edit `application/node/custom/your_node.lua`
2. Call `vne_reload_custom_nodes` (no args)
3. If `status: "success"` — node is live, open your test flow and run
4. If `status: "timeout"` — VNE may not be running or mcp_host.lua needs update

### Files involved
| File | Role |
|------|------|
| `application/framework/mcp_host.lua` | Flag watcher (edit once, restart VNE to activate) |
| `save/temp/_reload_custom_nodes.flag` | Trigger (written by MCP tool, consumed by mcp_host) |
| `save/temp/_reload_custom_nodes.result` | Response (written by mcp_host, read by MCP tool) |
| `tools/vne-mcp-server/vne_mcp_server.py` | MCP tool `vne_reload_custom_nodes` handler |

## Custom Pins

Template: `application/pin/custom/_自定义引脚模板.lua`

### Pin Definition Fields
| Field | Purpose |
|-------|---------|
| `type_id` | Unique pin type identifier (persisted in .flow!) |
| `display_name/name` | Editor display name |
| `icon_type` | Circle or diamond shape |
| `color` | Pin color |
| `default_name` | Default new-pin display name |
| `runtime.validate` | Pre-execution data validation |
| `can_accept` | Custom connection compatibility |
| `_on_tick_widgets` | Editor widget rendering |
| `on_load/on_save` | Custom serialization |
| `set_val/get_val` | Value get/set |

**WARNING**: `type_id` is persisted in .flow files. Never rename after creation.

## Custom Scenes

Template: `application/scene/_自定义场景模板.lua`

Use for: battles, mini-games, complex cutscenes, special input handling.

### Lifecycle
```lua
function MyScene:on_enter()         -- Entry
function MyScene:on_update(delta)   -- Per-frame (call Scene.on_update(self, delta) for base)
function MyScene:on_render()        -- Per-frame draw (call Scene.on_render(self) for base)
function MyScene:on_exit()          -- Exit
function MyScene:on_destroy()       -- Cleanup (call Scene.on_destroy(self) for base)
self:_finish_scene()                -- Return to flow
```

### Usage in Flow
File: `application/scene/custom_battle.lua`
Node value in switch_to_game_scene: `application.scene.custom_battle`

## Plugin System

Structure under `plugins/`:
```
plugins/my_game/
  manifest.json          ← auto-registration
  scene.lua              ← entry scene (must return class with new())
  node_def.lua           ← OPTIONAL: custom node display
  resources/
    texture/
    audio/
```

### manifest.json Minimum
```json
{
    "kind": "plugin",
    "api_version": 1,
    "id": "my_game",
    "display_name": "小游戏",
    "entry_point": "scene.lua",
    "resource_root": "resources",
    "node_type_id": "plug_my_game",
    "input_pins": [
        {"type_id": "flow", "key": "in"},
        {"type_id": "int", "key": "difficulty", "name": "难度", "default": 1}
    ],
    "output_pins": [
        {"type_id": "flow", "key": "out"},
        {"type_id": "int", "key": "score", "name": "得分"}
    ]
}
```

### Complete Plugin Scene
```lua
local Class = require("application.framework.class")
local Scene = require("application.framework.scene")

local MyPluginScene = Class.define("MyPluginScene", Scene)

function MyPluginScene:ctor(args)
    Class.call_super(MyPluginScene, self, "ctor")
    self.difficulty = tonumber(args.difficulty) or 1
    self.resources = args.resources
    self._output_values = { score = 0, completed = false }
end

function MyPluginScene:on_update(delta)
    Scene.on_update(self, delta)  -- REQUIRED for base functionality
end

function MyPluginScene:_finish()
    self._output_values.score = 100
    self._output_values.completed = true
    self:complete("out")  -- "out" = output pin key
end

-- Save/Load support (if "supports_save": true in manifest)
function MyPluginScene:can_save_now(context) return true end
function MyPluginScene:collect_plugin_state()
    return {schema_version=1, score=self.score, completed=self.completed}
end
function MyPluginScene:apply_plugin_state(state)
    self.score = tonumber(state.score) or 0
    self.completed = state.completed == true
    return true
end

return MyPluginScene
```

### Plugin Resource System
```lua
self.resources:find_texture("background")      -- reads resources.texture.background from manifest
self.resources:find_audio("music")             -- reads resources.audio.music
self.resources:get_declared("background")      -- get manifest-declared relative path
self.resources:resolve_path(path, "texture")   -- resolve to real path
```
Supported: texture (.png/.jpg/.webp/.tif/.avif), audio (.wav/.mp3/.ogg/.flac).
No built-in find_video/find_font/find_shader — use resource input pins instead.

### Plugin Pinning Rules
- `id` and `node_type_id` are persisted in .flow — never rename after release
- Pin `type_id` values must already be registered (custom pins go in application/pin/custom/)
- `entry_point`, `resource_root`, resource paths are plugin-relative (no `..` or absolute)
- At least one flow input + one flow output required

## WolfAndStar Terminal Command Pattern

WolfAndStar implements a computer terminal gameplay mechanic:

```lua
-- Flow nodes register valid commands
record_terminal_command("unlock gate")  
record_terminal_command("open gate")

-- Then launch the terminal scene with command lists
switch_to_game_scene(
    "application.scene.scene_computer_terminal",
    开屏文本 = 1,
    正确指令ID序列 = "unlock_gate,open_gate",  -- comma-separated!
    错误指令ID序列 = "",
    死亡场景ID = "",
    跳转指令ID列表 = ""
)
-- Outputs redirect based on which command player typed
```

## Node Grouper Plugin (plugins/node-grouper/)

Adds parent-child grouping to flow nodes. Solves the problem that VNE nodes
are flat with no hierarchy — accidental drags break layouts.

**Features:**
- "节点分组" node in right-click menu under "分组" category
- `imgui.NodeEditor.Comment()` renders visual container box
- Dragging group moves all child nodes within its bounds
- Lock toggle prevents children from being individually dragged
- Customizable title, size via right-click menu

**Key implementation details:**
- `on_update` in node_def.lua tracks position delta each frame
- Iterates `blueprint._node_pool` to find nodes within group bounds
- Applies same delta to children via `SetNodePosition`
- Runtime: simple pass-through scene (complete("out"))

**File structure:**
```
plugins/node-grouper/
├── manifest.json    — plugin registration (node_type_id: "node_group")
├── scene.lua        — runtime pass-through
├── node_def.lua     — editor behavior (comment box + child sync)
└── README.md
```

## Pre-Release Checklist (from official guide)
1. Custom node/pin filenames don't start with underscore
2. All type_ids / node_type_ids are unique
3. Plugin manifest.json parses correctly
4. Plugin scene.lua exists and returns class with new()
5. Plugin has ≥1 flow input + ≥1 flow output
6. Non-flow outputs written to self._output_values with matching keys
7. Private resources under resource_root (no absolute paths, no `..`)
8. supports_save → implement can_save_now + collect + apply
9. Test: enter → exit → output values → error logs → load recovery
10. Release build includes all custom scripts + plugin directories
