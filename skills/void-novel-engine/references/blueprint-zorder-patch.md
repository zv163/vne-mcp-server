# Blueprint Z-Order Patch: "提到最前 / 放回原位"

Patch for `application/framework/blueprint.lua` (line ~1577).
Adds a toggle menu item to every node's right-click context menu.

## What it does

- **提到最前**: Moves node to end of `_node_pool` (rendered last = on top)
- **放回原位**: Moves node to beginning of `_node_pool` (rendered first = behind everything)
- Toggle state stored per-node as `node._z_front`

## Patch Location

In `_draw_flow_context_popups()`, insert BEFORE the existing `self._node_menu:on_show_menu()` call:

```lua
-- === PATCH: 提到最前 / 放回原位 ===
if self._node_menu then
    imgui.Separator()
    local node = self._node_menu
    local is_front = rawget(node, "_z_front")
    if is_front then
        if imgui.MenuItem("放回原位") then
            node._z_front = false
            local pool = self._node_pool
            local nid = node._id:get()
            local ordered = {}
            for k, v in pairs(pool) do
                if k ~= nid then table.insert(ordered, {k, v}) end
            end
            table.sort(ordered, function(a,b) return a[1] < b[1] end)
            pool = {}
            pool[nid] = node
            for _, e in ipairs(ordered) do pool[e[1]] = e[2] end
            self._node_pool = pool
            _mark_flow_graph_dirty(self)
        end
    else
        if imgui.MenuItem("提到最前") then
            node._z_front = true
            local pool = self._node_pool
            local nid = node._id:get()
            pool[nid] = nil
            pool[nid] = node
            _mark_flow_graph_dirty(self)
        end
    end
    imgui.Separator()
end
-- === END PATCH ===
```

## Usage

Restart VNE editor after applying patch. Right-click any node → separator → "提到最前" / "放回原位" → separator → node's own menu.

## Limitations

- Uses `pairs()` iteration over `_node_pool` which may not guarantee stable ordering in all Lua versions
- "放回原位" moves to absolute front, not the original position
- Patch must be re-applied if blueprint.lua is updated
