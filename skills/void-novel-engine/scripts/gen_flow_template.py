#!/usr/bin/env python3
"""VNE .flow generator template — minimal skeleton to copy and extend."""
import json, os, uuid

# === CONFIG ===
# Fill in resource GUIDs from vne_list_resources
G = {
    "study": "FILL_ME",
    "style": "FILL_ME",
    "main_menu": "FILL_ME",
}

# === GENERATOR CORE ===
uid = [0]
nodes = []
links = []

def ni():
    uid[0] += 1
    return uid[0]

def pi():
    return ni()

def N(type_id, inputs, outputs, pos, psv=1):
    """Create a node. inputs: [(key, type_id, val?, name?), ...].
       outputs: [(key, type_id, name?), ...].
       Returns (output_map, input_map) where maps are {key: pin_id}."""
    nid = ni()
    il, im = [], {}
    for it in inputs:
        k, pt = it[0], it[1]
        v = it[2] if len(it) > 2 else None
        nm = it[3] if len(it) > 3 else None
        p = pi()
        o = {"id": p, "type_id": pt, "is_output": False, "key": k}
        if v is not None:
            o["val"] = v
        if nm:
            o["name"] = nm
        il.append(o)
        im[k] = p
    ol, om = [], {}
    for it in outputs:
        k, pt = it[0], it[1]
        nm = it[2] if len(it) > 2 else None
        p = pi()
        o = {"id": p, "type_id": pt, "is_output": True, "key": k}
        if nm:
            o["name"] = nm
        ol.append(o)
        om[k] = p
    nodes.append({
        "id": nid, "type_id": type_id, "position": pos,
        "pin_schema_version": psv,
        "input_pin_list": il, "output_pin_list": ol,
    })
    return om, im

def L(from_pin, to_pin):
    """Create a link between two pins."""
    links.append({"id": ni(), "output_pin_id": from_pin, "input_pin_id": to_pin})

def C(prev_flow, next_in, next_out=None):
    """Chain: link prev_flow → next_in, return next_out (or None)."""
    L(prev_flow, next_in)
    return next_out

def D(role, text, x, y):
    """Create a show_dialog_box node. Returns (in_pin, out_pin)."""
    o, i = N("show_dialog_box", [
        ("in", "flow"),
        ("role_text", "string", role),
        ("dialogue_text", "string", text),
        ("wait_interaction", "bool", True),
    ], [("out", "flow")], {"x": x, "y": y})
    return i["in"], o["out"]

# === BUILD FLOW ===
# 1. Entry
eo, ei = N("entry", [], [("out", "flow")], {"x": 0, "y": 0})
flow = eo["out"]

# 2. Set style
so, si = N("set_style", [
    ("in", "flow"),
    ("style", "style", {"guid": G["style"], "path_hint": "style/main.style"}),
], [("out", "flow")], {"x": 250, "y": 0})
flow = C(flow, si["in"], so["out"])

# 3. Add your nodes here — see references/flow-generation.md for node schemas
# Example dialog:
# di, do = D("角色", "对话内容", 500, 0)
# flow = C(flow, di, do)

# 4. Switch to main menu at end
_, sci = N("switch_scene", [
    ("in", "flow"),
    ("target", "string", "flow/主菜单.flow"),
], [], {"x": 1000, "y": 0})
L(flow, sci["in"])

# === WRITE & REGISTER ===
OUTPUT = "/mnt/d/A-Game/VoidNovelEngine/application/resources/flow/YOUR_FLOW.flow"
fj = {"max_uid": uid[0] + 10, "link_pool": links, "node_pool": nodes}
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(fj, f, ensure_ascii=False)
print(f"Written: {len(nodes)} nodes, {len(links)} links → {OUTPUT}")

# Now call vne_validate_flow, then vne_register_asset, then vne_refresh_assets
