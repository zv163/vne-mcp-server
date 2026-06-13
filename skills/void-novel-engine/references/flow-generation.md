# VNE .flow File Generation Guide

## Format

`.flow` is JSON with three top-level keys:
```json
{
  "max_uid": <highest-used-id>,
  "link_pool": [{ "id": N, "output_pin_id": N, "input_pin_id": N }, ...],
  "node_pool": [{ "id": N, "type_id": "...", "position": {"x":N,"y":N}, "pin_schema_version": N, "input_pin_list": [...], "output_pin_list": [...] }, ...]
}
```

## Critical Rules (crash if violated)

### 1. Pin keys MUST match node definitions
Every input and output pin (except `entry` outputs) MUST have a `"key"` field. Wrong keys cause immediate editor crash.

**Most common mistake**: `show_choice_button` outputs
- ❌ `route_1`, `route_2`, `route_3` — CRASH
- ✅ `choice_1`, `choice_2`, `choice_3`

### 2. merge_flow inputs need explicit keys
The `merge_flow` node definition does NOT auto-assign keys. Every input MUST have `"key": "in_1"` etc.
- ❌ No key → CRASH
- Avoid `merge_flow` entirely if unsure — duplicate endings per branch instead.

### 3. switch_background needs pin_schema_version: 2
- ❌ `pin_schema_version: 1` → may cause rendering issues
- ✅ `pin_schema_version: 2`

### 4. Foreground object pins MUST be connected
- `add_foreground` output `"foreground"` pin → `remove_foreground`/`move_foreground` input `"foreground"` pin
- Not connected = runtime failure (node can't find the object to act on)

## Node Reference (most common types)

### Dialog: `show_dialog_box`
```
Inputs: in(flow), role_text(string), dialogue_text(string), wait_interaction(bool, default=true)
Outputs: out(flow)
```

### Choice: `show_choice_button`
```
Inputs: in(flow), choice_text_1..5(string)
Outputs: choice_1..5(flow)  ← NOT route_1!
```

### Background: `switch_background` (psv=2)
```
Inputs: in(flow), texture(texture), fade_time(float), wait(bool)
Outputs: out(flow)
```

### Foreground: `add_foreground`
```
Inputs: in(flow), texture(texture), scale(float), position(vector2), fade_time(float), wait(bool)
Outputs: out(flow), foreground(object) ← connect to remove/move!
```

### Remove foreground: `remove_foreground`
```
Inputs: in(flow), foreground(object) ← MUST link from add_foreground.foreground!
Outputs: out(flow)
```

### Move foreground: `move_foreground`
```
Inputs: in(flow), foreground(object) ← MUST link from add_foreground.foreground!, position(vector2), duration(float), wait(bool)
Outputs: out(flow)
```

### Audio: `play_audio`
```
Inputs: in(flow), audio(audio), loop(bool), volume(float), fade_time(float)
Outputs: out(flow), token(string)
```

### Other common nodes
- `delay` — inputs: in(flow), seconds(float); outputs: out(flow)
- `set_style` — inputs: in(flow), style(style); outputs: out(flow)
- `clear_style` — inputs: in(flow); outputs: out(flow)
- `stop_all_audio` — inputs: in(flow), fade_time(float); outputs: out(flow)
- `switch_scene` — inputs: in(flow), target(string); outputs: none

## Canvas Size Limits

VNE editor flow graph view has a **hard limit of 80 nodes per .flow file**.

| Node count | Result |
|-----------|--------|
| 3–52 | Safe, opens fine |
| 82 | Borderline (may work, may freeze) |
| 127+ | Broken (black screen or crash) |

**Rule: never exceed 80 nodes.** For stories requiring more, split into
multiple scenes connected via `switch_scene`.

### Scene Splitting Pattern

When a story exceeds 80 nodes, split into separate .flow files:

```
主场景 (entry scene): all shared setup → choice
    ↓ choice_1              ↓ choice_2              ↓ choice_3
switch_scene("分支1.flow")  switch_scene("分支2.flow")  switch_scene("分支3.flow")
```

Each branch scene is a standalone .flow with its own:
`entry` → `set_style` → dialogues → ending → `stop_all_audio` → `clear_style` → `switch_scene("主菜单.flow")`

Example: a 127-node confession story splits into 4 scenes of 28–47 nodes each.

When generating large flows:
- Keep Y-span under 2000px
- Keep X-span under 3000px
- Stack branches HORIZONTALLY not vertically
- Use DY=48 for dialog nodes, DY=60 for others
- DX=240 between horizontal node columns

## Resource References

Resources in .flow use this format:
```json
{"guid": "fb764d1e-f9cc-4c76-a068-7a72f8091e99", "path_hint": "texture/study.png"}
```

Always use `vne_list_resources` to get the correct GUIDs before generating.

## Recommended Workflow

1. `vne_list_node_types` — see all available nodes and their pin schemas
2. Generate .flow JSON (use Python script)
3. `vne_validate_flow` — catch pin key errors BEFORE opening
4. `vne_register_asset` — create .meta + register in project.vne
5. `vne_refresh_assets` — clear MCP cache
6. Open in VNE editor
7. If black screen: reduce node count, compact layout, try `.vns` instead
