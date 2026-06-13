# dialog_line v3 — Combined Dialog Node for VNE

Replaces the 3-node chain (hide_dialog_box + play_audio + show_dialog_box)
with a single custom node. ~60% node reduction in dialogue-heavy scenes.

Node file: `application/node/custom/dialog_line.lua`

The node was built and debugged through 3 iterations:
- v1: Module name wrong (AudioManager ≠ AudioPlaybackManager), remove_object instead of hide()
- v2: Fixed module names, still had Common.default_font_reference (factory function, not font)
- v3: All fixes applied, verified against built-in show_dialog_box and hide_dialog_box source
  - `check_input` → `try_check_input` for optional prev_dialog (first node has no prev)

## Pin Schema (v3, verified)

| Pin | Direction | Type | Required | Default | Purpose |
|-----|-----------|------|----------|---------|---------|
| `in` | input | flow | yes | — | Upstream execution flow |
| `prev_dialog` | input | object | chain-dependent | — | Previous node's dialog_box (Billboard). First node leaves unconnected. |
| `role_text` | input | string | yes | — | Character name |
| `dialogue_text` | input | string | yes | — | Dialogue line text |
| `audio` | input | audio | no | — | Audio resource (optional). Connects to `audio` type pin. |
| `volume` | input | float | no | 0.8 | Playback volume 0-1 |
| `out` | output | flow | yes | — | Downstream execution flow |
| `dialog_box` | output | object | yes | — | Billboard object for next node. Type: dialog_box |

Note: `prev_dialog` and `dialog_box` both set `options = {object_type = "dialog_box"}`.

## Chain Pattern

```
[entry]
  out → dialog_line(A).in
dialog_line(A):  role="张晨", dialogue="我喜欢你很久了..."
  out → dialog_line(B).in
  dialog_box → dialog_line(B).prev_dialog
dialog_line(B):  role="小美", dialogue="...我..."
  out → dialog_line(C).in
  dialog_box → dialog_line(C).prev_dialog
dialog_line(C):  role="小美", dialogue="我也喜欢你。", audio=<bgm>
  out → switch_scene(menu)
```

**First node**: `prev_dialog` unconnected.
**Subsequent nodes**: MUST receive `prev_dialog` from previous node's `dialog_box`.

## Complete Runtime Logic (v3, production)

```lua
node.on_execute = function(self, scene)
    -- 1. Hide previous dialog (try_check_input → nil-safe, no abort on empty)
    local prev_db = NodeRuntimeHelper.try_check_input(self, "prev_dialog", "object")
    if prev_db and type(prev_db) == "table" and prev_db.hide then
        prev_db:hide(0.05)
    end

    -- 2. Optional audio (try_check_input — returns nil silently when pin is empty)
    -- check_resource would ABORT on nil for unconnected audio pins!
    local audio_ref = NodeRuntimeHelper.try_check_input(self, "audio", "audio")
    if audio_ref then
        local vol = math.max(0, math.min(1, NodeRuntimeHelper.check_float(self, "volume") or 0.8))
        AudioPlaybackManager.play(audio_ref, {
            loop_count = 0,
            volume = vol,
            fade_in_seconds = 0,
        })
    end

    -- 3. Show current dialog (same API as built-in show_dialog_box)
    local role_text = NodeRuntimeHelper.check_string(self, "role_text") or ""
    local dialogue_text = NodeRuntimeHelper.check_string(self, "dialogue_text") or ""
    local convert_color = NodeRuntimeHelper.convert_imvec4_to_sdl_color
    local default_font = GlobalContext.font_wrapper_sdl

    local dialog_box = Billboard.new(
        role_text, dialogue_text,
        140, 760, 1640,                           -- x, y, width
        default_font, default_font,                -- role_font, dialogue_font
        convert_color(imgui.ImVec4(1, 0.9, 0.65, 1)),    -- role_color
        convert_color(imgui.ImVec4(0.96, 0.96, 0.96, 1)), -- dialogue_color
        convert_color(imgui.ImVec4(0.06, 0.09, 0.13, 0.86)), -- bg_color
        0.2,                                      -- fade_in time
        nil,                                      -- background image
        RuntimeLayout.scale_font_size(28),        -- role font size
        RuntimeLayout.scale_font_size(25)         -- dialogue font size
    )
    scene:add_object(dialog_box, object_id, 50)
    NodeRuntimeHelper.set_output(self, "dialog_box", dialog_box)
end

node.on_execute_update = function(self, scene, delta)
    local dialog_box = scene:find_object(object_id)
    if dialog_box and dialog_box._progress == 1 then
        NodeRuntimeHelper.wait_interact_to_next_node(self, "out")
    end
end
```

## Required Modules

```lua
local Common = require("application.framework.builtin_node_common")
local AudioPlaybackManager = require("application.framework.audio_playback_manager")
local RuntimeLayout = require("application.framework.runtime_layout_context")
local GlobalContext = require("application.framework.global_context")
```

## Critical API Pitfalls

| Wrong | Right | Why error occurs |
|-------|-------|------------------|
| `require("...audio_manager")` | `require("...audio_playback_manager")` | AudioManager.lua does not exist in framework/ |
| `scene:remove_object(prev_db)` | `prev_db:hide(0.05)` | remove_object has no animation; hide() does fade-out tween |
| `Common.default_font_reference` as Billboard arg | `GlobalContext.font_wrapper_sdl` | default_font_reference is a factory function, not a FontWrapper |
| `Common.sdl.SDL_Color(r,g,b,a)` | `NodeRuntimeHelper.convert_imvec4_to_sdl_color(imvec4)` | Inconsistent with built-in node convention |
| `check_input(self, "prev_dialog")` | `try_check_input(self, "prev_dialog", "object")` | check_input ABORTS on nil — first node has no prev! |
| `check_resource(self, "prev_dialog", "object")` | `try_check_input(self, "prev_dialog", "object")` | Object pins need check_input/try_check_input, not check_resource |
| No type check on prev_db | `type(prev_db) == "table" and prev_db.hide` | First node has nil prev_dialog — must guard |

## Node Definition (category/order)

```lua
type_id = "dialog_line"
name = "对话行"
icon_id = "chat-quote-fill"
color = imgui.ImVec4(imgui.ImColor(0, 160, 200, 255).value)
category = "演出控制"
category_order = 1
order = 11
keywords = {"对话", "合并", "音频", "dialog", "combined"}
```

## Test Flow

`_dialog_line_test.flow` (6 nodes, validated OK):
```
entry → set_style → dialog_line(张晨) → dialog_line(小美, audio=bgm.wav) → dialog_line(林雪) → switch_scene(menu)
```

## Comparison

| Approach | Nodes/line | Hide wiring | Audio/line | Role name | Node count (3-line scene) |
|----------|:---:|:---:|:---:|:---:|:---:|
| show_dialog_box + hide + play_audio | 3 | manual (2 links) | extra node | yes | 11+ |
| show_subtitle + play_audio | 2 | auto | extra node | prefix only | 8 |
| show_subtitle (text only) | 1 | auto | no | prefix only | 5 |
| **dialog_line** | **1** | **built-in** | **built-in** | **yes** | **5** |

## Lifecycle Notes

- Hot-reload via `vne_reload_custom_nodes` MCP tool (v1.3.0+). Write flag → mcp_host.lua detects → definition_loader.load(). No restart needed after initial mcp_host.lua activation.
- One-time: restart VNE after first installing mcp_host.lua watcher and v1.3.0 MCP server.
- The node appears in right-click menu under 演出控制 → 对话行
- All 3 dialog_line warnings in validate_flow are expected ("unknown type_id 'dialog_line' (may be custom)")
- The first dialog_line in a chain has prev_dialog pin unconnected (try_check_input gracefully returns nil)
