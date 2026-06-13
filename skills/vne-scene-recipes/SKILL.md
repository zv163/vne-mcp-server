---
name: vne-scene-recipes
description: Ready-to-use VNE scene templates + UI/Style design patterns. Based on WolfAndStar analysis and VNE3 official PDF guides (UIDesigner, StyleDesigner, ProjectExample).
category: software-development
triggers:
  - Building a new VNE scene
  - Creating menu/ending/checkpoint scenes
  - Designing UI layouts (.ui files)
  - Configuring global styles (.style files)
  - Implementing save/load systems in VNE
  - Adding gameplay mechanics to VNE flows
---

# VNE Scene Recipes & UI/Style Design

## Scene Cleanup Chain (MUST follow this order)

Every scene that shows dialog boxes must clean up before transitioning:

```
hide_dialog_box  ← MUST connect dialog_box object from last show_dialog_box!
  → delay(1.5)
  → stop_all_audio(fade=0.55)
  → clear_style
  → switch_scene("target") or switch_to_game_scene(...)
```

**Without `hide_dialog_box`, the last dialog box persists on screen even after scene transitions.**

## Dialogue Pattern: ALWAYS use show_subtitle

`show_dialog_box` CANNOT be chained — each call creates a persistent billboard.
Use `show_subtitle` for all dialogue. Prefix character names with `【】`:

```
show_subtitle("【张晨】我喜欢你！")     ← character dialogue
show_subtitle("放学铃声响起…")          ← narration (no prefix)
```

`show_subtitle` auto-replaces previous text. No hide needed between lines.
Node count: 1 per line. Verified working pattern from WolfAndStar (42 nodes).

### Subtitle pin schema
```
Inputs:  in(flow), 文本(string), 字号(int)=28, 字符时间间隔(float)=0.03,
         屏幕底部距离(float)=60, 等待互动(bool)=true
Outputs: out(flow)
```

## Recipe 0: Dialogue Pattern (READ FIRST)

**show_dialog_box does NOT chain.** Each call creates an independent object that stacks.
For sequential dialogue, use show_subtitle with character name prefix `【角色名】`:

```
entry → set_style → switch_background → play_audio → delay
  → show_subtitle("【张晨】今天一定要说出来。")
  → show_subtitle("【小美】哟，张晨，你还没走啊？")
  → show_subtitle("这是旁白，没有角色名。")
  → choice → ...
```

If you must use show_dialog_box, insert hide_dialog_box between each:
```
show(A) → hide(A.dialog_box, fade=0.3) → show(B) → hide(B.dialog_box) → ...
```
Requires TWO connections: flow (out→in) AND object (dialog_box→dialog_box).

## Scene Templates (all <80 nodes)

### Recipe 1: Linear Narrative Scene (with proper dialog lifecycle)

```
entry → set_style → switch_background(bg, fade=0.5, wait=false)
  → play_audio(BGM, loop=9999, vol=0.3, fade=0.7)
  → delay(0.5)
  → show_dialog_box("", "Opening...", wait=true)
    → hide_dialog_box(prev.dialog_box)          ← CRITICAL: hide before next
      → show_dialog_box("Char", "Line 2...")
        → hide_dialog_box(prev.dialog_box)
          → ... (repeat for all dialogues)
            → hide_dialog_box(final.dialog_box)  ← final hide
              → delay(1.5) → stop_all_audio → clear_style → switch_scene("next")
```

**Dialog chaining rule**: Every `show_dialog_box` creates an independent object.
Between each pair, insert `hide_dialog_box` with TWO connections:
- Flow: show.out → hide.in
- Object: show.dialog_box → hide.dialog_box

## Recipe 1: Linear Narrative Scene
```
entry → set_style → switch_background(bg, fade=0.5, wait=false)
  → play_audio(BGM, loop=9999, vol=0.3, fade=0.7)
  → delay(0.5)
  → show_subtitle_segments (intro, 2-4 segments)
  → show_subtitle × N (main text, wait=true)
  → hide_dialog_box(dialog_box=last_show_dialog_box.out.dialog_box)
  → stop_all_audio(fade=0.55) → clear_style → switch_scene("next")
```

### Recipe 2: Choice Scene with Merge
```
entry → set_style → switch_background → play_audio
  → show_subtitle("", "What will you do?")
  → show_choice_button(choice_text_1="A", choice_text_2="B")
    ├→ choice_1 → show_subtitle("A") → merge_flow
    └→ choice_2 → show_subtitle("B") → merge_flow
      → save_global("choice", value) → switch_scene("next")
```

### Recipe 3: Menu Scene
```
entry → stop_all_audio(fade=1) → play_audio("menu_bgm", loop=9999)
  → switch_to_game_scene("application.scene.scene_start_menu")
    → 默认 → switch_scene("chapter_0")
```

### Recipe 4: Terminal/Computer Scene (WolfAndStar pattern!)
```
entry → show_subtitle("A computer screen flickers...")
  → record_terminal_command("help")
  → record_terminal_command("open door")
  → switch_to_game_scene(
      "application.scene.scene_computer_terminal",
      开屏文本=1,
      正确指令ID序列="help,open_door",
      错误指令ID序列="",
      死亡场景ID="",
      跳转指令ID列表=""
    )
    → 默认 → show_subtitle("You typed correctly!")
    → 指令1 → show_subtitle("First command executed")
    → 指令2 → show_subtitle("Second command executed")
```

### Recipe 5: Death Scene with Checkpoint
```
entry → stop_all_audio(fade=1)
  → switch_to_game_scene("application.scene.scene_chapter_transition", 开屏文本=10)
    → 默认 → show_subtitle("You died...")
      → hide_subtitle → delay(1)
      → show_choice_button("回到检查点", "返回主菜单")
        ├→ choice_1 → switch_scene("checkpoint")
        └→ choice_2 → switch_scene("menu")
```

### Recipe 6: Inventory Check
```
entry → load_global("hasKeyCard")
  → has_inventory_item("keycard_tt", 1)
    → show_subtitle("You use the keycard")
    → add_inventory_item("access_granted", 1)
```

### Recipe 7: Black Overlay Cinematic
```
entry → show_subtitle("...")
  → show_black_overlay(fade_time=0.5, wait_fade=true)
  → show_overlay_subtitle("A voice echoes in darkness...")
  → hide_black_overlay
  → show_subtitle("The light returns.")
```

## Style System (.style files)

### Style Domains (from official guide)
| Domain | Controls |
|--------|----------|
| 对话框 | Role name, dialogue text, position, width, fonts, sizes, colors, bg image, fade time |
| 字幕 | Font, size, color, bottom distance, character interval |
| 分支按钮 | Font, text/hover/bg/border colors, spacing, padding, min width |
| 着色器 | Background, foreground, video, global post-process shaders |

### Style Inheritance
```
Base.style ← Chapter_01.style (parent=Base.style)
```
Child only overrides changed fields. Unset fields fall through to parent → built-in defaults.

### Flow usage
```
set_style → (.style resource)
...
clear_style  → (removes current style)
```
Node-level pin values ALWAYS override style defaults.

### Custom Style Domains
For custom nodes/scenes that need shared visual config. Add domain → add fields with stable English keys. Custom nodes read via StyleManager.

## UI System (.ui files)

### UI Components
| Category | Components | Use |
|----------|-----------|-----|
| Display | 面板, 文本, 图片 | Backgrounds, titles, labels |
| Interactive | 按钮, 切换按钮, 进度条 | Menu buttons, toggles, volume bars |
| Save/Load | 存档网格 | Save/load slot grids |
| Layout | 垂直/水平/叠加容器, 滚动视图, 网格容器 | Organize child components |

### UI-Node Bridge
| Flow Node | Purpose |
|-----------|---------|
| `show_ui` | Open UI, continue flow (HUD, overlays) |
| `call_ui` | Open UI, WAIT for close (menus, dialogs) |
| `close_ui` | Close specific UI |
| `ui_on_click/hover` | Component event listeners |

### Button Actions
Buttons can have built-in actions: close_ui, open_ui, quick_save, quick_load, skip, auto, rollback, open_save_panel, open_load_panel. Or "无动作" to let flow nodes handle events.

## Multi-Scene Architecture (WolfAndStar pattern)

Split by background change. Each .flow file <60 nodes.
Use `switch_scene` between scenes.

```
Scene 1: 教室 (study.png) — 42 nodes
  → switch_scene("Scene 2")
Scene 2: 樱花树 (mainroom.png) — 33 nodes  
  → choice → switch_scene("Scene 3/4/5")
Scene 3-5: 结局分支 — 46-57 nodes each
  → switch_scene("menu")
```

## Node Layout Rules

Staircase pattern for easy right-click access:
```
DialogChain helper: sx=cx; each node sx-=20 (left-down diagonal)
Section gap: DX=360 between logical sections
Spacing: DY=50 between nodes
```

## Dialog Chain Pattern

`show_dialog_box` does NOT auto-replace. Use show→hide→show chain:
```
show(A) → hide(A.dialog_box, fade=0.05) → show(B)
```
Connect BOTH: flow (out→in) AND object (dialog_box→dialog_box).
hide_dialog_box params: fade_out_time=0.05, wait_interaction=false.

## Scene Splitting Rules

1. **Split at every background change** — each new background = its own .flow file
2. **Keep <60 nodes per scene** (safe margin below the 80-node limit)
3. **Chain scenes with `switch_scene("flow/next.flow")`**
4. **Clean state on transition**: `hide_dialog_box`→`stop_all_audio`→`clear_style`→`switch_scene`
5. **hide_dialog_box params**: `fade_out_time=0.05, wait_interaction=false`

## Dialog Lifecycle

`show_dialog_box` does NOT auto-replace. Use `show_subtitle` for chained text (prefix: `【角色名】`).
For show_dialog_box, always pair with hide_dialog_box connected via BOTH flow AND dialog_box object pin.

## Validation Checklist
1. `vne_validate_flow` — all errors fixed
2. Nodes < 80
3. `choice_N` output keys ✓
4. Integer pin IDs in links ✓
5. switch_background psv=2 ✓
6. foreground pins connected ✓
7. `vne_register_asset` ✓
8. `vne_refresh_assets` ✓
