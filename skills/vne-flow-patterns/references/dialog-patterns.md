# VNE Dialog Patterns — Programmatic Flow Generation

> **New**: `dialog_line` custom node collapses 3-node show→hide→show chain into 1 node.
> See [references/dialog-line.md](references/dialog-line.md) for pin schema, runtime logic, and comparison.
> This is the recommended approach for all new dialogue-heavy scenes.

## The DialogChain Helper (legacy)

When generating .flow files programmatically, use this pattern to ensure every dialogue is properly
hidden before the next appears. This is the working pattern evolved through multiple iterations.

```python
def DialogChain(cx, cy, lines, in_flow):
    """Chain dialogues with hide_dialog_box between each.
    lines = [(role, text), ...]
    in_flow = upstream flow pin (output from previous node)
    Returns (last_flow_out, last_dialog_box_pin, new_cy)."""
    pf = in_flow
    prev_db = None
    for role, text in lines:
        if prev_db is not None:
            # Hide previous dialog before showing new one
            hi, ho, hdb = Hide(cx, cy)
            L(pf, hi)      # flow: previous → hide.in
            L(prev_db, hdb) # object: previous dialog_box → hide.dialog_box
            pf = ho
            cy += DY
        
        so, sdb, si = Show(role, text, cx, cy)
        L(pf, si)          # flow: upstream → show.in
        pf = so
        prev_db = sdb
        cy += DY
    
    return pf, prev_db, cy
```

## The Bug: First dialogue not connected to upstream

**Original broken code:**
```python
def DialogChain(cx, cy, lines):
    first_in = None
    ...
    return first_in, prev_out, prev_db, cy

# Caller:
di, f, last_db, cy = DialogChain(cx, cy, [...])
# di (first_in) was NEVER connected to the upstream flow!
```

**Fix:** Pass `in_flow` as a parameter and connect internally.

## Full example: Scene with background, audio, foreground, dialogue chain

```python
def build_scene(N, L, Show, Hide, DialogChain, Delay, AddFG, SwitchBG, ...):
    # Setup
    eo, ei = N("entry", [], [("out", "flow")], {"x": 0, "y": 0})
    f = eo["out"]
    
    so, si = N("set_style", [...], [("out", "flow")], {"x": 200, "y": 0})
    L(f, si["in"]); f = so["out"]
    
    do, di = SwitchBG(guid, "texture/bg.png", 0.5, 460, 0)
    L(f, di); f = do
    
    do, di = PlayAudio(guid, "audio/bgm.wav", True, 0.30, 0.70, 720, 0)
    L(f, di); f = do
    
    do, di = Delay(0.5, 980, 0)
    L(f, di); f = do
    
    # Dialogue chain — in_flow=f ensures upstream is connected
    cx = 1240; cy = 0
    f, last_db, cy = DialogChain(cx, cy, [
        ("", "Opening narration..."),
        ("角色", "Character dialogue..."),
    ], f)  # ← pass current flow
    
    # Foreground
    fo, ffg, fi = AddFG(guid, "texture/girl.png", 0.88, 340, 45, cx, cy)
    L(f, fi); f = fo; cy += DY
    
    do, di = Delay(0.45, cx, cy)
    L(f, di); f = do; cy += DY
    
    # More dialogue
    f, last_db, cy = DialogChain(cx, cy, [
        ("", "More text..."),
        ("角色", "More dialogue..."),
    ], f)
    
    # Final hide + cleanup + exit
    hi, ho, hdb = Hide(cx, cy)
    L(f, hi); L(last_db, hdb); f = ho
    
    do, di = Delay(1.5, cx, cy)
    L(f, di); f = do; cy += DY
    
    so1, si1 = N("stop_all_audio", [("in", "flow"), ("fade_time", "float", 0.55)], [("out", "flow")], {"x": cx, "y": cy})
    L(f, si1["in"]); f = so1["out"]
    
    co, ci = N("clear_style", [("in", "flow")], [("out", "flow")], {"x": cx + DX, "y": cy})
    L(f, ci["in"]); f = co["out"]
    
    _, sci = N("switch_scene", [("in", "flow"), ("target", "string", "flow/next.flow")], [], {"x": cx + DX*2, "y": cy})
    L(f, sci["in"])
```

## Scene splitting rule: new background = new scene

Split .flow files at every background change, not just at the 80-node limit:

```
校园恋爱_01_教室.flow    (study.png,  42 nodes)
校园恋爱_02_樱花树.flow   (mainroom.png, 33 nodes)
校园恋爱_03_勇敢.flow     (no bg setup, 46 nodes)
校园恋爱_04_递信.flow     (no bg setup, 47 nodes)  
校园恋爱_05_逃避.flow     (no bg setup, 57 nodes)
```

Each background change triggers a `switch_scene` to the next file.
This ensures clean visual state on every transition.
