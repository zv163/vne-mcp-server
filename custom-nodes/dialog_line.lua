--[[
  dialog_line v3 — 合并对话节点
  一个节点 = 隐藏上一句(淡出) + 播放音频(可选) + 显示当前对话(淡入)
  链式连接: nodeA.dialog_box → nodeB.prev_dialog
  大幅减少节点数，消除独立的 hide_dialog_box 和 play_audio 节点
  
  v3 修复:
  - 字体使用 GlobalContext.font_wrapper_sdl（而非工厂函数）
  - v2: 音频模块名修正、hide()替代remove_object
]]

local Common = require("application.framework.builtin_node_common")
local AudioPlaybackManager = require("application.framework.audio_playback_manager")
local RuntimeLayout = require("application.framework.runtime_layout_context")
local GlobalContext = require("application.framework.global_context")

local imgui = Common.imgui
local Billboard = Common.Billboard
local NodeRuntimeHelper = Common.NodeRuntimeHelper

return Common.make_definition({
    type_id = "dialog_line",
    icon_id = "chat-quote-fill",
    color = imgui.ImVec4(imgui.ImColor(0, 160, 200, 255).value),
    name = "对话行",
    comment = "合并：隐藏上句 + 播放音频 + 显示当前对话。dialog_box 链式连接。",
    category = "演出控制",
    category_order = 1,
    order = 11,
    menu_visible = true,
    keywords = {"对话", "合并", "音频", "dialog", "combined"},
}, function(ctx)
    local node = ctx:create_base_node()
    local builder = ctx.builder
    local convert_color = NodeRuntimeHelper.convert_imvec4_to_sdl_color
    local default_font = GlobalContext.font_wrapper_sdl

    builder:add_input({key = "in", type_id = "flow"})
    builder:add_input({key = "prev_dialog", type_id = "object", name = "上一句对话框", options = {object_type = "dialog_box"}})
    builder:add_input({key = "role_text", type_id = "string", name = "角色", options = {width_input = 80}})
    builder:add_input({key = "dialogue_text", type_id = "string", name = "台词", options = {width_input = 200}})
    builder:add_input({key = "audio", type_id = "audio", name = "音频(可选)"})
    builder:add_input({key = "volume", type_id = "float", name = "音量", default = 0.8})

    builder:add_output({key = "out", type_id = "flow"})
    builder:add_output({key = "dialog_box", type_id = "object", name = "对话框", options = {object_type = "dialog_box"}})

    local object_id <const> = string.format("dialog_line_%d", node._id:get())

    node.on_execute = function(self, scene)
        -- 1. 隐藏上一句的对话框（淡出动画，0.05秒）
        -- 用 try_check_input：第一个节点无上一句时返回 nil，不报错
        local prev_db = NodeRuntimeHelper.try_check_input(self, "prev_dialog", "object")
        if prev_db and type(prev_db) == "table" and prev_db.hide then
            prev_db:hide(0.05)
        end

        -- 2. 播放音频（可选，无音频时静默跳过）
        local audio_ref = NodeRuntimeHelper.try_check_input(self, "audio", "audio")
        if audio_ref then
            local vol = math.max(0, math.min(1, NodeRuntimeHelper.check_float(self, "volume") or 0.8))
            AudioPlaybackManager.play(audio_ref, {
                loop_count = 0,
                volume = vol,
                fade_in_seconds = 0,
            })
        end

        -- 3. 显示当前对话（使用与 show_dialog_box 一致的 Billboard API）
        local role_text = NodeRuntimeHelper.check_string(self, "role_text") or ""
        local dialogue_text = NodeRuntimeHelper.check_string(self, "dialogue_text") or ""

        local dialog_box = Billboard.new(
            role_text,                                      -- name
            dialogue_text,                                  -- dialogue
            140,                                            -- x
            760,                                            -- y
            1640,                                           -- width
            default_font,                                   -- role_font (FontWrapper)
            default_font,                                   -- dialogue_font
            convert_color(imgui.ImVec4(1, 0.9, 0.65, 1)),  -- role_color (gold, SDL_Color)
            convert_color(imgui.ImVec4(0.96, 0.96, 0.96, 1)), -- dialogue_color (white)
            convert_color(imgui.ImVec4(0.06, 0.09, 0.13, 0.86)), -- bg_color (dark)
            0.2,                                            -- fade_in time
            nil,                                            -- background image
            RuntimeLayout.scale_font_size(28),              -- role font size
            RuntimeLayout.scale_font_size(25)               -- dialogue font size
        )
        scene:add_object(dialog_box, object_id, 50)
        NodeRuntimeHelper.set_output(self, "dialog_box", dialog_box)
    end

    node.on_execute_update = function(self, scene, delta)
        local dialog_box = scene:find_object(object_id)
        if dialog_box and dialog_box._progress == 1 then
            NodeRuntimeHelper.wait_interact_to_next_node(self, "out")
        end
    end

    return node
end)
