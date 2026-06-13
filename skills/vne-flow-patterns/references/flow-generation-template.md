# VNE .flow Generation Template

This is the canonical Python script for generating VNE .flow files programmatically.
It encodes all the hard-won pin schema knowledge from reverse-engineering VNE3.

## Correct Node Pin Schemas

### add_foreground (psv=2)
```
Inputs:  in(flow), scale(float), position(vector2), texture(texture), fade_time(float), wait(bool), shader(shader)
Outputs: out(flow), foreground(object)
```
**psv MUST be 2. Pin order: in→scale→pos→texture→fade→wait→shader. Missing shader = runtime error.**

### switch_background (psv=2)
```
Inputs:  in(flow), texture(texture), fade_time(float), wait(bool), shader(shader)
Outputs: out(flow)
```

### show_dialog_box (psv=1)
```
Inputs:  in(flow), role_text(string), dialogue_text(string), wait_interaction(bool)
Outputs: out(flow), dialog_box(object)
```
**dialog_box output MUST connect to hide_dialog_box.dialog_box input for proper cleanup.**

### show_subtitle (psv=1)
```
Inputs:  in(flow), 文本(string), 字号(int)=28, 字符时间间隔(float)=0.03, 屏幕底部距离(float)=60, 等待互动(bool)=true
Outputs: out(flow)
```
**Auto-replaces previous subtitle. Use for chained dialogue. No hide needed.**

### show_choice_button (psv=1)
```
Inputs:  in(flow), choice_text_1..5(string)
Outputs: choice_1..5(flow)  ⚠️ NOT route_1..5!
```

### hide_dialog_box (psv=1)
```
Inputs:  in(flow), dialog_box(object), fade_out_time(float), wait_interaction(bool)
Outputs: out(flow)
```
**MUST receive dialog_box object from show_dialog_box output. Two connections required.**

## Known Limits
- 80 nodes per .flow file maximum (VNE editor freezes/crashes beyond)
- Split at background changes (switch_background → new scene)
- show_dialog_box cannot chain — use show_subtitle or hide between each

## Generation Checklist
1. vne_list_node_types → verify pin keys
2. Generate .flow with Python
3. vne_validate_flow → fix all errors
4. vne_register_asset → auto-register
5. vne_refresh_assets → clear cache
