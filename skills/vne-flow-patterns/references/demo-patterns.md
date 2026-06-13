# VNE Demo Flow Analysis — Key Findings

## Dialogue System: show_dialog_box is NOT chainable

**Confirmed by testing**: `show_dialog_box` creates independent billboard objects.
Consecutive calls result in TEXT STACKING — old text remains visible.
The official demo flows confirm this:

| Flow | Dialogue method | Pattern |
|------|----------------|---------|
| 主菜单.flow | `show_subtitle` only | Chain without hide |
| 存档演示.flow | `show_subtitle` + `hide_subtitle` | Chain without hide |
| 音频播控演示.flow | `show_dialog_box` → `hide_dialog_box` → `show_subtitle` | ONE dialog box, then switch |
| 界面演示.flow | `show_subtitle` + `hide_subtitle` | Chain without hide |

**No demo flow chains multiple show_dialog_box calls.** The only show_dialog_box
usage is a single instance followed by explicit hide_dialog_box, then switch to subtitle.

## Correct Patterns

### For chained dialogue (WolfAndStar pattern):
```
show_subtitle("text 1") → show_subtitle("text 2") → show_subtitle("text 3")
```
Each call auto-replaces. Character names as 【prefix】.

### For one-off character dialog:
```
show_dialog_box(role, text) → hide_dialog_box(dialog_box ref) → show_subtitle(...)
```
Two connections required: flow + object reference.

## Node Schema Verification

All schemas verified against existing .flow files in the project:
- add_foreground: psv=2, needs shader pin, pin order matters
- switch_background: psv=2, needs shader pin
- show_dialog_box: outputs dialog_box(object) — required for hide
- hide_dialog_box: needs BOTH flow in and dialog_box(object) connected
- show_subtitle: single text object, auto-replaces

## 80-Node Limit

Confirmed: VNE editor cannot handle >80 nodes per .flow file.
Split scenes at logical boundaries using switch_scene.
