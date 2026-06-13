---
name: vne-flow-patterns
description: VNE flow graph patterns, node type reference, scene structures, and best practices learned from analyzing WolfAndStar (a published VNE3 game) and official VNEdev3 PDF guides.
category: software-development
triggers:
  - Creating or editing VNE .flow files
  - Generating flow graphs programmatically
  - Debugging VNE flow graph issues
  - Learning VNE node types and pin schemas
  - Building visual novel scenes with VNE
---

# VNE Flow Patterns & Node Reference

Comprehensive reference for VoidNovelEngine 3, derived from:
- WolfAndStar (16 flow files, 108 nodes in workstation_01 alone, 40+ node types)
- Official VNEdev3 PDF guides (8 documents, 53 pages total)

## 80-Node Limit (CRITICAL)

**VNE editor freezes/crashes when a .flow file exceeds ~80 nodes.**
WolfAndStar's largest scene is workstation_01 at 108 nodes (DEV2), but DEV3 has this limit.
Always split larger flows into multiple scenes using `switch_scene`.

## DEV2 vs DEV3 Pin Key Differences

WolfAndStar uses DEV2 format where pins have **no explicit keys** (all show as `?`).
Our DEV3 requires **every pin to have a `key` field**. VNE3 nodes use key-based lookup.

## Complete Node Type Reference

### Flow Control
| type_id | Purpose | Key Inputs | Key Outputs | Terminal? |
|---------|---------|------------|-------------|:--:|
| `entry` | Scene start | none | flow (no key) | - |
| `switch_scene` | Jump to .flow by filename | in(flow), target(string) | none | **YES** |
| `switch_to_game_scene` | Jump to Lua scene with command routing | in(flow), scene(string), 开屏文本(int), 正确指令(str), 错误指令(str), 死亡场景(str), 跳转指令(str) | 默认, 指令1-3, 退出 (5 outputs) | No |
| `merge_flow` | Rejoin branches | 3 unnamed (name=流程1,2,3) | flow | No |
| `extend_pins` | Dynamic pin addition | in(flow), object | flow | No |
| `delay` | Pause seconds | in(flow), seconds(float) | out(flow) | No |
| `branch` | If/else | in(flow), condition(bool) | true_route, false_route | No |

### Dialogue System
| type_id | WolfAndStar Usage | Key Params |
|---------|------------------|------------|
| `show_subtitle` | 42 nodes in workstation_01 | 文本(string), 字体=font, 字号=25, 颜色≈white, 底部距离=40, 字符间隔=0.03, 等待互动=true |
| `show_subtitle_segments` | 18 nodes — multi-part text | 文本段数(int), 文本1-4(string) |
| `hide_subtitle` | Clean up before choices | in(flow) only |
| `show_dialog_box` | Character-name dialog (DEV3) | role_text, dialogue_text, position, width, fade_time, wait |
| `show_overlay_subtitle` | Text on black overlay (workstation_06) | same as subtitle on black bg |
| `show_overlay_subtitle_segments` | Segmented overlay text | same as segments on black bg |

### Audio System (channel-based)
| type_id | WolfAndStar Example |
|---------|---------------------|
| `play_audio` | "amb_doomdrones_deep_cavern" loop=9999 vol=1 fade=1 — returns channel(int) |
| `play_audio` | "Gate Open 3-1" loop=0 vol=1 fade=0 — one-shot SFX |
| `stop_audio` | channel=-1 (all), fade=1 |
| `stop_all_audio` | fade_time |
| `fade_audio_volume` | Smooth vol change (workstation_05/06) |
| `set_audio_volume` | Instant vol change |

### Visual System
| type_id | WolfAndStar Details |
|---------|---------------------|
| `switch_background` | pin_schema_version=2, texture ref |
| `add_foreground` | Complex scene composition — "bg_area_1", "body_1-4", "head_1-3", "icon_4", "tips_1" |
| `remove_foreground` | 14 nodes in workstation_01 — connects to add_foreground output |
| `move_foreground` | Animate position |
| `show_black_overlay` | fade_time, wait_fade (workstation_06) |
| `hide_black_overlay` | Paired with show |
| `show_letterboxing` | Cinematic bars (ProjectExample guide) |
| `hide_letterboxing` | Remove bars |
| `play_video` | "fallen" video in dead_01.flow |
| `transition_fade_in` | Fade in effect |
| `transition_fade_out` | Fade out effect |

### Choice System
| type_id | WolfAndStar Pattern |
|---------|---------------------|
| `show_choice_button` | 1-2 choices (not all 5). Text: "撕下便利贴", "查看电脑", "检查随身物品" |
| Choice styling: | font=font, size=30, colors=muted lavender/white/dark-navy/gray, spacing=20, padding={100,12}, bottom=250, min_width=400 |

**CRITICAL**: Output keys MUST be `choice_1`..`choice_5`, NOT `route_1`..`route_5`.

### State & Persistence
| type_id | WolfAndStar Keys | Pattern |
|---------|------------------|---------|
| `save_global` | "hasReadTips", "AMB" | key(string) → value(object) |
| `load_global` | "hasReadTips", "AMB" | key(string) — 3 outputs: flow(success), flow(fail?), object(value) |
| `save_game` | Auto-save checkpoints | slot_id, resume_flow_id |
| `quick_save` | Single-slot quick save | |
| `quick_load` | Quick load | has success/failed outputs |

### Inventory & Logic
| type_id | Purpose |
|---------|---------|
| `has_inventory_item` | Conditional gate — item_id(string), quantity(int) |
| `add_inventory_item` | Add to inventory |
| `bool` | Literal boolean value node (WolfAndStar uses one!) |

### Gameplay Mechanic: Terminal Commands
```
record_terminal_command("unlock gate")  → registers valid CLI command
record_terminal_command("open gate")    → registers another
switch_to_game_scene(
  scene="application.scene.scene_computer_terminal",
  正确指令ID序列="unlock_gate,open_gate"  → comma-separated!
)
```

### UI Integration Nodes
| type_id | Purpose |
|---------|---------|
| `show_ui` | Open UI, continue flow (HUD, overlays) |
| `call_ui` | Open UI, WAIT for close (menus, dialogs) |
| `close_ui` | Close specific UI |
| `ui_on_click` | Listen for button click |
| `ui_on_hover` | Listen for hover |
| `ui_on_open` | UI opened callback |
| `ui_on_close` | UI closed callback |

### Environment Nodes
| type_id | Purpose |
|---------|---------|
| `set_style` | Apply .style file |
| `clear_style` | Remove style |
| `wait_interaction` | Wait for click |

## WolfAndStar Scene Structure

### workstation_01.flow (108 nodes)
```
entry
  → show_subtitle_segments × N (player wakes up, explores)
  → show_subtitle × N (narration)
  → show_choice_button ("检查随身物品")
    → branch content
    → show_choice_button ("撕下便利贴" / "查看电脑")
      → branch A: record_terminal_command("unlock gate") + "open gate"
      → branch B: more exploration
  → load_global("hasReadTips") / load_global("AMB")
  → save_global("hasReadTips") / save_global("AMB")
  → switch_to_game_scene("application.scene.scene_computer_terminal")
  → switch_to_game_scene("application.scene.scene_chapter_transition")
  → switch_scene("workstation_02")
```

### Scene Transition Architecture
```
menu.flow → switch_to_game_scene("scene_start_menu")
  → 默认 → switch_scene("chapter_0")
    → switch_scene("workstation_01")
      → switch_scene("workstation_02")
      → dead_01.flow (death → choice → back to checkpoint or menu)
    → end_escape.flow → switch_to_game_scene("scene_ending")
```

## UI Styling Constants (from WolfAndStar)

### Subtitle
```json
{ "底部距离": 40, "字体": "font", "字号": 25,
  "字符间隔": 0.03, "等待互动": true,
  "颜色": {"r":0.95,"g":0.95,"b":0.95,"a":1.0} }
```

### Choice Button
```json
{ "字体": "font", "字号": 30, "按钮间隔": 20,
  "按钮内边距": {"x":100,"y":12}, "底部距离": 250,
  "最小宽度": 400,
  "默认颜色": {"r":0.58,"g":0.55,"b":0.69,"a":1.0},
  "高亮": {"r":1.0,"g":1.0,"b":1.0,"a":1.0},
  "背景": {"r":0.23,"g":0.27,"b":0.40,"a":0.78},
  "边框": {"r":0.47,"g":0.47,"b":0.47,"a":1.0} }
```

## Complete Pin Schema Reference (from verified VNE3 .flow files)

Deviating from these causes runtime errors. Pin ORDER matters.

### switch_background (psv=2)
```
Inputs:  in(flow), texture(texture), fade_time(float), wait(bool), shader(shader)
Outputs: out(flow)
```

### add_foreground (psv=2) ⚠️
```
Inputs:  in(flow), scale(float), position(vector2), texture(texture), fade_time(float), wait(bool), shader(shader)
Outputs: out(flow), foreground(object)
```
**psv MUST=2. Missing shader → runtime error. Pin order: in→scale→pos→texture→fade→wait→shader.**

### remove_foreground (psv=1)
```
Inputs:  in(flow), foreground(object), fade_time(float), wait(bool)
Outputs: out(flow)
```

### move_foreground (psv=1)
```
Inputs:  in(flow), foreground(object), position(vector2), duration(float), wait(bool)
Outputs: out(flow)
```

### show_choice_button (psv=1)
```
Outputs: choice_1..5(flow)  ⚠️ NOT route_1..5!
```

### show_dialog_box (psv=1) ⚠️ MUST output dialog_box
```
Outputs: out(flow), dialog_box(object)  ← REQUIRED for hide_dialog_box!
```

### hide_dialog_box — TWO connections required
```
Inputs:  in(flow), dialog_box(object), fade_out_time(float), wait_interaction(bool)
Outputs: out(flow)
Pattern: show_dialog_box.out → hide.in  AND  show.dialog_box → hide.dialog_box
Without the object connection, the dialog persists forever.
```

### switch_scene (psv=1) ⚠️ TERMINAL — no outputs

## Dialogue Text: CRITICAL — show_dialog_box CANNOT be chained

`show_dialog_box` creates an independent Billboard object per call. **Consecutive calls STACK — old text persists visibly under new text.** Each node gets its own `object_id` based on `node._id`, so they never replace each other. This is by design.

### The only show_dialog_box pattern that works
```
show_dialog_box (A)
  out → hide_dialog_box.in              (flow link)
  dialog_box → hide_dialog_box.dialog_box  (object link — MANDATORY)
hide_dialog_box (fade=0.3, wait=false)
  out → show_dialog_box (B).in
```
**Without the object link, `hide_dialog_box` has nothing to target and the dialog persists forever.**

### Preferred: Use `show_subtitle` for all chained dialogue
```python
show_subtitle("【张晨】我喜欢你！")  # role as prefix, auto-replaces
show_subtitle("【林雪】……我也是。")  # replaces previous instantly
show_subtitle("就这样，夕阳下的告白…")  # narration, no prefix
```
`show_subtitle` manages a single text object per scene — each call replaces the previous. This is how WolfAndStar delivers ALL dialogue (42 `show_subtitle` nodes in workstation_01). All VNE demo flows use `show_subtitle` for chained text.

### When to use show_dialog_box
Only for one-off character dialog that you explicitly hide:
```
show_dialog_box(role="讲师", text="这是教程。") 
  → hide_dialog_box(dialog_box connected!) 
  → show_subtitle(...)
```

### show_subtitle pin schema
```
Inputs: in(flow), 文本(string), 字体(font), 字号(int) default=25,
        字符时间间隔(float) default=0.03, 屏幕底部距离(float) default=40,
        颜色(color), 等待互动(bool) default=true
Outputs: out(flow)
```

### Scene splitting strategy
Split at every background change, not just at the 80-node limit. Each background = its own scene file. This keeps files small and ensures visual state is clean on every transition. Use `switch_scene("flow/next_scene.flow")` between scenes.

## Dialog Lifecycle (CRITICAL)

### show_dialog_box does NOT auto-replace
Each `show_dialog_box` creates an independent Billboard object. Chaining them
causes text to accumulate/stack — old text remains visible under new text.
**Do NOT chain show_dialog_box calls directly.**

### Two correct patterns:

**Pattern A: show_subtitle for chained dialogue (recommended)**
`show_subtitle` auto-replaces the previous subtitle. Use for sequential text.
Prefix character names: `【张晨】我喜欢你！`. WolfAndStar uses 42 show_subtitle nodes.

**Pattern B: show_dialog_box + hide_dialog_box (for character-name dialogs)**
Requires TWO connections:
```
show(A).out → hide.in              (flow)
show(A).dialog_box → hide.dialog_box  (object reference — REQUIRED!)
hide.out → show(B).in
```
Without the dialog_box object connection, hide_dialog_box has no target.
Use `fade_out_time=0.3, wait_interaction=false` for seamless transitions.

### Pattern C: Mixed approach
Use show_dialog_box for first line with character name, then switch to
show_subtitle for subsequent lines. This avoids node bloat from hide nodes.

### Pattern D: dialog_line custom node (RECOMMENDED — 60% node reduction)
A single custom node that combines hide_previous + play_audio(optional) + show_current.
One `dialog_line` node replaces a 3-node chain (hide_dialog_box + play_audio + show_dialog_box).

**Pin schema (v3, verified):**
```
Inputs:  in(flow), prev_dialog(object, type=dialog_box), role_text(string),
         dialogue_text(string), audio(audio, optional), volume(float, default=0.8)
Outputs: out(flow), dialog_box(object, type=dialog_box)
```
Note: `prev_dialog` MUST use `object_type = "dialog_box"` so the editor enforces
correct pin connections. First node in chain leaves `prev_dialog` unconnected.

**Chain pattern:**
```
dialog_line(A).dialog_box → dialog_line(B).prev_dialog
dialog_line(A).out → dialog_line(B).in
```

**How it works (v3 implementation):**
1. `try_check_input(self, "prev_dialog", "object")` → gets Billboard or nil (first node has no prev — check_input would crash!)
2. `prev_db:hide(0.05)` — calls Billboard:hide() for smooth fade-out tween
3. `try_check_input(self, "audio", "audio")` → if connected, calls `AudioPlaybackManager.play()`. check_resource would ABORT on empty pin.
4. `Billboard.new(role, text, x=140, y=760, w=1640, fonts, colors, fade=0.2, ...)` — creates new dialog
5. `scene:add_object(dialog_box, object_id, 50)` — registers on layer 50
6. `set_output(self, "dialog_box", dialog_box)` — exposes for next node's prev_dialog
7. `on_execute_update`: waits for `dialog_box._progress == 1` then `wait_interact_to_next_node`

**Key APIs (do NOT deviate):**
| API | Purpose | Wrong alternative |
|-----|---------|-------------------|
| `AudioPlaybackManager` | Play audio | ~~AudioManager~~ (doesn't exist) |
| `Billboard:hide(0.05)` | Fade out previous | ~~scene:remove_object()~~ (no animation) |
| `GlobalContext.font_wrapper_sdl` | Default font | ~~Common.default_font_reference~~ (factory, not font) |
| `NodeRuntimeHelper.convert_imvec4_to_sdl_color` | Color conversion | ~~raw SDL_Color()~~ (inconsistent) |
| `try_check_input(self, "prev_dialog", "object")` | Read optional object input | ~~check_input~~ (aborts on nil!) |
| `try_check_input(self, "audio", "audio")` | Read optional audio resource | ~~check_resource~~ (aborts on nil!) |

**Node file:** `application/node/custom/dialog_line.lua` (80 lines, v3)
**Category:** 演出控制 → 对话行 (color: cyan, icon: chat-quote-fill)
**Custom node lifecycle:** Edit .lua → `vne_reload_custom_nodes` (hot-reload, no restart). First install needs one VNE restart to load mcp_host.lua watcher. See vne-custom-extensions skill → Hot-Reload section.

**Advantages over show_subtitle:** Retains dialog box styling (role name, colors, frame).
**Advantages over raw show_dialog_box:** 1 node vs 3; no manual hide wiring; audio inline.
**Advantages over subtitle + separate audio:** Audio stays with its line; no drift risk.

## 80-Node Limit (TESTED)

| Nodes | Result |
|:--:|------|
| 21 | ✓ opens |
| 50 | ✓ opens |
| 80 | ✓ opens |
| 127 | ✗ black screen |
**Hard limit: 80 nodes per .flow file. Split by background change into scenes <60.**

## Node Layout Rules (ZV preference)

- **Staircase**: left-down diagonal, each node shifts DS=20px LEFT from previous
- **Section gap**: DX=360 between logical sections (背景切换 = new section)
- **Dialog chain spacing**: DY=50 vertical between nodes
- This exposes each node's right edge for easy right-click access

## show_dialog_box Lifecycle (CRITICAL)

`show_dialog_box` does NOT auto-replace previous dialog boxes. Each call creates
a separate Billboard object that stacks. To properly chain dialogues:

**Option A (manual, 3 nodes per line):**
```
show_dialog_box(A)
  out → hide_dialog_box.in           (flow connection)
  dialog_box → hide_dialog_box.dialog_box  (object connection)
hide_dialog_box
  out → show_dialog_box(B).in
```

**Option B (RECOMMENDED: dialog_line custom node, 1 node per line):**
Use `dialog_line` from `application/node/custom/dialog_line.lua`. One node = hide + audio + show.
Chain via `prev_dialog`/`dialog_box` object pins. See Pattern D above for pin schema.

**hide_dialog_box must receive BOTH:**
1. Flow connection from the show it's hiding
2. Object connection (`dialog_box` pin → `dialog_box` pin)

**hide_dialog_box recommended params:** `fade_out_time=0.05, wait_interaction=false`
(0.05s provides enough time for the render cycle to clear the old dialog without visible flicker)

**Alternative: use `show_subtitle`** — auto-replaces text, no hide needed. Use `【角色名】`
prefix for character dialogue. This is how WolfAndStar does it (42 subtitle nodes).

## Pitfalls (Battle-Tested)

1. **choice output keys**: Must be `choice_1`..`choice_5`, NOT `route_1` → CRASH
2. **add_foreground psv**: Must be 2, + `shader` pin. Missing → "纹理未设置" runtime error
3. **switch_background**: Must have `shader` pin
4. **80-node limit**: Exceeding causes freeze — split into multiple scenes
5. **Dict-as-pin in links**: Links must use integer pin IDs, never dicts (output_map vs output_map['out'])
6. **hide_dialog_box needs TWO connections**: flow (out→in) AND object (dialog_box→dialog_box)
7. **show_dialog_box doesn't auto-replace**: Each creates separate Billboard. Chain with hide between.
8. **show_subtitle auto-replaces**: Better for chained text. Use `【角色名】` prefix for names.
9. **hide_dialog_box fade_out_time**: Use 0.05 (not 0.0, not 0.3) for clean transition
10. **switch_scene is terminal**: No output pins — flow execution ends here
11. **foreground connections**: add_foreground output MUST link to remove/move input
12. **Audio channels**: play_audio returns channel(int) → connect to stop_audio channel input
13. **merge_flow inputs**: 3 inputs with name="流程1/2/3", need explicit keys in DEV3
14. **Pin order matters**: add_foreground expects in→scale→position→texture→fade→wait→shader
15. **DialogChain helper must connect in_flow**: First dialogue's flow input must receive upstream flow
16. **dialog_line custom node**: After editing `dialog_line.lua`, call `vne_reload_custom_nodes` MCP tool to hot-reload (no restart needed). First install requires one VNE restart to activate mcp_host.lua watcher.
17. **dialog_line prev_dialog chain**: First dialog_line in chain has no prev_dialog (leave unconnected). Subsequent nodes MUST receive prev_dialog from previous node's dialog_box output, or text stacks/overlaps.
18. **hide_dialog_box needs dialog_box object**: show_dialog_box MUST output a `dialog_box` (object) pin AND connect it to hide_dialog_box's dialog_box input. Without this object connection, the dialog persists even after scene transitions.
19. **dialog_line optional pins use try_check_input**: Both `prev_dialog` and `audio` must use `try_check_input` (NOT `check_input`/`check_resource`). Those abort on nil, which happens on the first node (no prev_dialog) or when audio isn't connected.
20. **hot-reload requires flow reopen**: After `vne_reload_custom_nodes`, open flow tabs still use old node definitions. Close and reopen the .flow file (or touch it on disk to trigger auto-reload) for new definitions to take effect.
