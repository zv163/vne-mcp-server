#!/usr/bin/env python3
"""VNE .flow graph generator helper.
Usage: import this module and call build_flow(nodes) to generate .flow JSON.

Example:
    from gen_flow import FlowBuilder
    fb = FlowBuilder()
    fb.resource("study", "fb764d1e-...", "texture/study.png")
    e = fb.entry()
    s = fb.set_style(e, "style_guid", "style/main.style")
    bg = fb.switch_background(s, "study", 0.5)
    dlg = fb.dialog(bg, "角色", "台词")
    fb.switch_scene(dlg, "flow/主菜单.flow")
    fb.write("path/to/output.flow")
"""

import json

class FlowBuilder:
    def __init__(self):
        self._uid = 0
        self._nodes = []
        self._links = []
        self._resources = {}  # name -> {"guid", "path_hint"}

    def _nid(self):
        self._uid += 1
        return self._uid

    def _pin(self):
        return self._nid()

    def resource(self, name, guid, path_hint):
        """Register a resource by name for later reference."""
        self._resources[name] = {"guid": guid, "path_hint": path_hint}

    def _res(self, name):
        """Get resource reference dict."""
        return self._resources[name]

    def _node(self, type_id, inputs, outputs, pos=None):
        """inputs: [(key, type_id, val?, name?), ...]
           outputs: [(key, type_id, name?), ...]
           Returns output_pin_id (the primary "out" or first output)."""
        nid = self._nid()
        inp_list = []
        inp_map = {}
        for item in inputs:
            key, ptype = item[0], item[1]
            val = item[2] if len(item) > 2 else None
            name = item[3] if len(item) > 3 else None
            pid = self._pin()
            p = {"id": pid, "type_id": ptype, "is_output": False, "key": key}
            if val is not None:
                p["val"] = val
            if name is not None:
                p["name"] = name
            inp_list.append(p)
            inp_map[key] = pid
        out_list = []
        out_map = {}
        for item in outputs:
            key, ptype = item[0], item[1]
            name = item[2] if len(item) > 2 else None
            pid = self._pin()
            p = {"id": pid, "type_id": ptype, "is_output": True, "key": key}
            if name is not None:
                p["name"] = name
            out_list.append(p)
            out_map[key] = pid
        self._nodes.append({
            "id": nid, "type_id": type_id, "position": pos or {"x": 0, "y": 0},
            "pin_schema_version": 1,
            "input_pin_list": inp_list, "output_pin_list": out_list,
        })
        return out_map, inp_map

    def _link(self, from_pin, to_pin):
        self._links.append({
            "id": self._nid(),
            "output_pin_id": from_pin,
            "input_pin_id": to_pin,
        })

    def _chain(self, prev_out, next_in):
        """Link prev output to next input, return next output pin."""
        self._link(prev_out, next_in)

    # ---- Node builders ----

    def entry(self, pos=None):
        """Create entry node. Returns output flow pin id."""
        out, _ = self._node("entry", [], [("out", "flow")],
                           pos or {"x": -32, "y": -600})
        return out["out"]

    def set_style(self, prev_flow, style_name, pos=None):
        """prev_flow: output pin id from previous node."""
        out, inp = self._node("set_style", [
            ("in", "flow"),
            ("style", "style", self._res(style_name), "样式"),
        ], [("out", "flow")], pos)
        self._link(prev_flow, inp["in"])
        return out["out"]

    def switch_background(self, prev_flow, tex_name, fade_time=0.5, wait=False, pos=None):
        out, inp = self._node("switch_background", [
            ("in", "flow"),
            ("texture", "texture", self._res(tex_name), "纹理"),
            ("fade_time", "float", fade_time, "淡入时间"),
            ("wait", "bool", wait, "等待互动"),
        ], [("out", "flow")], pos)
        self._link(prev_flow, inp["in"])
        return out["out"]

    def play_audio(self, prev_flow, audio_name, loop=True, volume=1.0, fade_time=0.0, pos=None):
        out, inp = self._node("play_audio", [
            ("in", "flow"),
            ("audio", "audio", self._res(audio_name), "音频"),
            ("loop", "bool", loop, "循环"),
            ("volume", "float", volume, "音量"),
            ("fade_time", "float", fade_time, "淡入时间"),
        ], [("out", "flow"), ("token", "string", "播放令牌")], pos)
        self._link(prev_flow, inp["in"])
        return out["out"]

    def dialog(self, prev_flow, role, text, wait=True, pos=None):
        out, inp = self._node("show_dialog_box", [
            ("in", "flow"),
            ("role_text", "string", role, "角色文本"),
            ("dialogue_text", "string", text, "内容文本"),
            ("wait_interaction", "bool", wait, "等待互动"),
        ], [("out", "flow")], pos)
        self._link(prev_flow, inp["in"])
        return out["out"]

    def add_foreground(self, prev_flow, tex_name, scale=1.0, pos_vec=None,
                       fade_time=0.3, wait=False, node_pos=None):
        out, inp = self._node("add_foreground", [
            ("in", "flow"),
            ("texture", "texture", self._res(tex_name), "纹理"),
            ("scale", "float", scale, "缩放"),
            ("position", "vector2", pos_vec or {"x": 340, "y": 45}, "位置"),
            ("fade_time", "float", fade_time, "淡入时间"),
            ("wait", "bool", wait, "等待互动"),
        ], [("out", "flow"), ("foreground", "object", "前景")], node_pos)
        self._link(prev_flow, inp["in"])
        return out["out"], out["foreground"]

    def remove_foreground(self, prev_flow, fade_time=0.3, wait=False, pos=None):
        out, inp = self._node("remove_foreground", [
            ("in", "flow"),
            ("foreground", "object", None, "前景"),
            ("fade_time", "float", fade_time, "淡出时间"),
            ("wait", "bool", wait, "等待互动"),
        ], [("out", "flow")], pos)
        self._link(prev_flow, inp["in"])
        return out["out"]

    def move_foreground(self, prev_flow, target_pos, duration=0.35, wait=False, pos=None):
        out, inp = self._node("move_foreground", [
            ("in", "flow"),
            ("foreground", "object", None, "前景"),
            ("position", "vector2", target_pos, "目标位置"),
            ("duration", "float", duration, "时长"),
            ("wait", "bool", wait, "等待互动"),
        ], [("out", "flow")], pos)
        self._link(prev_flow, inp["in"])
        return out["out"]

    def delay(self, prev_flow, seconds, pos=None):
        out, inp = self._node("delay", [
            ("in", "flow"), ("seconds", "float", seconds, "秒数"),
        ], [("out", "flow")], pos)
        self._link(prev_flow, inp["in"])
        return out["out"]

    def choice(self, prev_flow, texts, pos=None):
        """texts: list of 2-3 strings. Returns {route_1: pin, route_2: pin, route_3: pin}."""
        inputs = [("in", "flow")]
        for i, t in enumerate(texts[:3]):
            inputs.append((f"choice_text_{i+1}", "string", t, f"分支文本{i+1}"))
        outputs = [(f"route_{i+1}", "flow", f"分支{i+1}") for i in range(len(texts))]
        out, inp = self._node("show_choice_button", inputs, outputs, pos)
        self._link(prev_flow, inp["in"])
        return out

    def merge_flow(self, *branch_flows, pos=None):
        """Join 2-3 branch flows into one. Returns merged output pin."""
        inputs = [("in", "flow")]
        for i in range(len(branch_flows)):
            inputs.append((f"in_{i+1}", "flow"))
        out, inp = self._node("merge_flow", inputs, [("out", "flow")], pos)
        for i, bf in enumerate(branch_flows):
            self._link(bf, inp[f"in_{i+1}"])
        return out["out"]

    def stop_all_audio(self, prev_flow, fade_time=0.5, pos=None):
        out, inp = self._node("stop_all_audio", [
            ("in", "flow"), ("fade_time", "float", fade_time),
        ], [("out", "flow")], pos)
        self._link(prev_flow, inp["in"])
        return out["out"]

    def clear_style(self, prev_flow, pos=None):
        out, inp = self._node("clear_style", [("in", "flow")], [("out", "flow")], pos)
        self._link(prev_flow, inp["in"])
        return out["out"]

    def switch_scene(self, prev_flow, target_flow_path, pos=None):
        """Terminal node — switches to another flow scene."""
        _, inp = self._node("switch_scene", [
            ("in", "flow"),
            ("target", "string", target_flow_path, "目标场景"),
        ], [], pos)
        self._link(prev_flow, inp["in"])

    # ---- Output ----

    def build(self):
        return {
            "max_uid": self._uid + 10,
            "link_pool": self._links,
            "node_pool": self._nodes,
        }

    def write(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.build(), f, ensure_ascii=False)
        return len(self._nodes), len(self._links)
