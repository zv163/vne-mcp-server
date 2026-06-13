# VNE .flow Node Graph Format

The `.flow` file is a JSON-serialized node graph. It is the primary format for VNE's visual flow designer (流程脚本视图).

## Top-Level Structure

```json
{
  "max_uid": <int>,       // highest ID used (nodes, pins, links all share the same ID space)
  "link_pool": [...],     // connections between output pins and input pins
  "node_pool": [...]      // the nodes themselves
}
```

IDs must be unique across all three categories. The `max_uid` field should be set to the highest allocated ID + a small buffer (e.g., +10).

## Nodes

Each node:

```json
{
  "id": <int>,
  "type_id": "<string>",       // e.g. "show_dialog_box", "switch_background"
  "position": {"x": <float>, "y": <float>},
  "pin_schema_version": 1,     // always 1 in current VNE version
  "input_pin_list": [...],
  "output_pin_list": [...]
}
```

### Input Pins

```json
{
  "id": <int>,
  "type_id": "<string>",    // "flow", "string", "float", "bool", "texture", "audio", "vector2", "color", "object", "style", "font", "int"
  "is_output": false,
  "key": "<string>",        // semantic key: "in", "role_text", "texture", etc.
  "val": <any>,             // OPTIONAL: default value (only present when pin has a value)
  "name": "<string>"        // OPTIONAL: display name in editor
}
```

### Output Pins

```json
{
  "id": <int>,
  "type_id": "<string>",
  "is_output": true,
  "key": "<string>",        // "out", "route_1", "foreground", "token", etc.
  "name": "<string>"        // OPTIONAL: display name
}
```

## Links

```json
{
  "id": <int>,
  "output_pin_id": <int>,   // source (from a node's output_pin_list)
  "input_pin_id": <int>     // destination (from a node's input_pin_list)
}
```

Links always go from an output pin to an input pin.

## Resource References

Resources are referenced by GUID + path hint:

```json
{"guid": "fb764d1e-f9cc-4c76-a068-7a72f8091e99", "path_hint": "texture/study.png"}
```

This appears as the `val` on input pins of type `texture`, `audio`, `font`, `style`, etc.

### Common Pin Types for Resources

| Resource Type | Pin type_id | val format |
|--------------|-------------|------------|
| Texture (PNG/JPG) | `texture` | `{guid, path_hint}` |
| Audio (WAV/MP3) | `audio` | `{guid, path_hint}` |
| Style (.style) | `style` | `{guid, path_hint}` |
| Font (TTF/OTF) | `font` | `{guid, path_hint}` |
| Scene (.flow) | `string` | `"flow/主菜单.flow"` (plain string for switch_scene target) |

## Key Node Type Reference

### Flow Control
| type_id | Inputs | Outputs | Notes |
|---------|--------|---------|-------|
| `entry` | (none) | `out` (flow) | Flow entry point, always node id=1 |
| `branch` | `in` (flow), `condition` (bool) | `true_route` (flow), `false_route` (flow) | Conditional branch |
| `switch_scene` | `in` (flow), `target` (string) | (none) | Switch to another flow, terminal node |
| `merge_flow` | `in_1`, `in_2`, `in_3` (all flow) | `out` (flow) | Join multiple branches, 3 inputs |
| `delay` | `in` (flow), `seconds` (float) | `out` (flow) | Wait N seconds |

### Presentation (演出控制)
| type_id | Key Inputs | Key Outputs | Notes |
|---------|-----------|-------------|-------|
| `show_dialog_box` | `role_text` (string), `dialogue_text` (string), `wait_interaction` (bool, default true) | `out` (flow), `dialog_box` (object) | Essential; pin_schema_version=1 |
| `show_choice_button` | `choice_text_1/2/3` (string) | `route_1/2/3` (flow) | 3-choice branch; no "out" pin |
| `switch_background` | `texture` (texture), `fade_time` (float), `wait` (bool) | `out` (flow) | |
| `add_foreground` | `texture` (texture), `scale` (float), `position` (vector2), `fade_time` (float), `wait` (bool) | `out` (flow), `foreground` (object) | |
| `move_foreground` | `foreground` (object), `position` (vector2), `duration` (float), `wait` (bool) | `out` (flow) | |
| `remove_foreground` | `foreground` (object), `fade_time` (float), `wait` (bool) | `out` (flow) | |
| `set_style` | `style` (style resource) | `out` (flow) | |
| `clear_style` | (only `in` flow) | `out` (flow) | |

### Audio
| type_id | Key Inputs | Key Outputs |
|---------|-----------|-------------|
| `play_audio` | `audio` (audio), `loop` (bool), `volume` (float), `fade_time` (float) | `out` (flow), `token` (string) |
| `stop_all_audio` | `fade_time` (float) | `out` (flow) |

## Vector2 Format

```json
{"x": 340, "y": 45}
```

## Programmatic Generation

When creating .flow files programmatically:
1. Start `max_uid` from 0, increment for every node, pin, and link
2. Use pin_schema_version=1 for all nodes
3. Most nodes have an `in` (flow) input and `out` (flow) output
4. `show_choice_button` outputs to `route_1/2/3` — no general `out`
5. `switch_scene` has no outputs (terminal)
6. Dialogues typically only need `role_text`, `dialogue_text`, `wait_interaction` — omit style pins to use defaults from `set_style`
7. Resource references go on input pins as `val`, not output pins
8. `foreground` pins on `remove_foreground`/`move_foreground` are `object` type — the runtime resolves them by connection, so `val` is null

## merge_flow Node

The `merge_flow` node has 3 flow inputs (`in_1`, `in_2`, `in_3`) and 1 flow output (`out`). It passes through whichever branch executed. Use it to join choice branches into a common ending sequence.
