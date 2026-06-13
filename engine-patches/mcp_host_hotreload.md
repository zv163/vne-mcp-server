# Engine Patch: Hot-Reload Custom Nodes

**Target File**: `application/framework/mcp_host.lua`  
**Requires**: VNE 0.1.0-dev.3+  
**Purpose**: Eliminates VNE restart when editing custom node `.lua` files.

## What It Does

Watches for a trigger file (`save/temp/_reload_custom_nodes.flag`) each frame. When detected:
1. Deletes the flag
2. Calls `definition_loader.load()` to reload ALL node/pin definitions
3. Writes result to `save/temp/_reload_custom_nodes.result`

## How to Apply

Open `application/framework/mcp_host.lua` and find the `MCPHost.update` function. 
In the `update` function, right after the console log flush block (around line 416), insert:

```lua
    -- ── Hot-reload custom nodes: check for trigger flag file ──
    -- MCP tool vne_reload_custom_nodes writes this flag; we detect it,
    -- call definition_loader.load() to reload ALL node/pin definitions,
    -- then write a result file.
    local RELOAD_FLAG = "save/temp/_reload_custom_nodes.flag"
    local RELOAD_RESULT = "save/temp/_reload_custom_nodes.result"
    if NativeIO.file_exists(RELOAD_FLAG) then
        NativeIO.remove_file(RELOAD_FLAG)
        local ok, err = pcall(function()
            local DefinitionLoader = require("application.framework.definition_loader")
            DefinitionLoader.load()
        end)
        if ok then
            LogManager.log("✓ 自定义节点已热重载", "success")
            NativeIO.write_text(RELOAD_RESULT, "success")
        else
            local err_msg = tostring(err or "unknown")
            LogManager.log("✗ 自定义节点热重载失败: " .. err_msg, "error")
            NativeIO.write_text(RELOAD_RESULT, "error: " .. err_msg)
        end
    end
```

**Important**: After hot-reloading, close and reopen any `.flow` files that use the 
custom nodes — existing node instances retain the old definition.

## Usage

1. Edit `application/node/custom/your_node.lua`
2. Run MCP tool: `vne_reload_custom_nodes`
3. Close and reopen affected `.flow` files in VNE
4. Test — no VNE restart needed
