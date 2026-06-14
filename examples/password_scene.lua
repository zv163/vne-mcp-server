--[[
  密码输入场景 v2 — 鼠标点击数字键盘
  密码: 5613
  使用鼠标点击屏幕上的数字按钮，避免键盘被 VNE 引擎拦截
]]

local rl = Engine.Raylib

local Class = require("application.framework.class")
local Scene = require("application.framework.scene")

local PasswordScene = Class.define("PasswordScene", Scene)

local CORRECT_PASSWORD = "5613"
local MAX_INPUT = 4

-- 按钮布局
local BTN_SIZE = 72
local BTN_GAP = 12
local GRID_COLS = 3
local PAD_START_X = 0  -- 动态计算
local PAD_START_Y = 0

function PasswordScene:ctor()
    Class.call_super(PasswordScene, self, "ctor")
    self._input = ""
    self._finished = false
    self._elapsed = 0
    self._error_flash = 0
    self._success_flash = 0
end

function PasswordScene:on_enter()
    self._input = ""
    self._finished = false
    self._elapsed = 0
    self._error_flash = 0
    self._success_flash = 0
end

function PasswordScene:_button_rect(row, col)
    local x = PAD_START_X + col * (BTN_SIZE + BTN_GAP)
    local y = PAD_START_Y + row * (BTN_SIZE + BTN_GAP)
    return rl.Rectangle(x, y, BTN_SIZE, BTN_SIZE)
end

function PasswordScene:_is_in_rect(mx, my, rect)
    return mx >= rect.x and mx <= rect.x + rect.width
       and my >= rect.y and my <= rect.y + rect.height
end

function PasswordScene:_draw_button(rect, text, color, text_color)
    -- 按钮背景
    rl.DrawRectangleRounded(rect, 0.15, 8, color)
    -- 文字
    local tw = rl.MeasureText(text, 32)
    local tx = rect.x + (rect.width - tw) / 2
    local ty = rect.y + (rect.height - 32) / 2
    rl.DrawText(text, math.floor(tx), math.floor(ty), 32, text_color)
end

function PasswordScene:on_update(delta)
    Class.call_super(PasswordScene, self, "on_update", delta)

    if self._finished then return end

    self._elapsed = self._elapsed + delta

    if self._error_flash > 0 then
        self._error_flash = self._error_flash - delta
    end
    if self._success_flash > 0 then
        self._success_flash = self._success_flash - delta
        if self._success_flash <= 0 and not self._finished then
            self:_finish_scene()
            return
        end
    end

    -- ESC 返回
    if rl.IsKeyPressed(256) then
        self:_finish_scene()
        return
    end

    -- 鼠标点击检测
    if not self:is_runtime_pointer_pressed() then return end

    local mx = rl.GetMouseX()
    local my = rl.GetMouseY()

    -- 数字按钮: 1-9 在 3x3 网格, 0 在下方居中
    local digits = {"1","2","3","4","5","6","7","8","9"}
    for i, d in ipairs(digits) do
        local row = math.floor((i-1) / GRID_COLS)
        local col = (i-1) % GRID_COLS
        if self:_is_in_rect(mx, my, self:_button_rect(row, col)) then
            if #self._input < MAX_INPUT then
                self._input = self._input .. d
            end
            return
        end
    end

    -- 0 按钮 (row 3, col 1)
    if self:_is_in_rect(mx, my, self:_button_rect(3, 1)) then
        if #self._input < MAX_INPUT then
            self._input = self._input .. "0"
        end
        return
    end

    -- 退格按钮 (row 3, col 0)
    if self:_is_in_rect(mx, my, self:_button_rect(3, 0)) then
        if #self._input > 0 then
            self._input = self._input:sub(1, -2)
        end
        return
    end

    -- 确认按钮 (row 3, col 2)
    if self:_is_in_rect(mx, my, self:_button_rect(3, 2)) then
        if #self._input > 0 then
            if self._input == CORRECT_PASSWORD then
                self._success_flash = 1.0
            else
                self._input = ""
                self._error_flash = 1.5
            end
        end
        return
    end
end

function PasswordScene:on_render()
    local w = rl.GetScreenWidth()
    local h = rl.GetScreenHeight()

    -- 计算键盘起始位置（居中）
    local pad_w = GRID_COLS * BTN_SIZE + (GRID_COLS - 1) * BTN_GAP
    local pad_h = 4 * BTN_SIZE + 3 * BTN_GAP
    PAD_START_X = math.floor((w - pad_w) / 2)
    PAD_START_Y = math.floor((h - pad_h) / 2) + 30

    -- 背景
    rl.ClearBackground(rl.Color(12, 16, 28, 255))

    -- 顶部标题区域
    local title = "🔒 请输入密码"
    local title_w = rl.MeasureText(title, 36)
    rl.DrawText(title, w//2 - title_w//2, PAD_START_Y - 100, 36, rl.Color(200, 210, 230, 255))

    -- 密码显示框
    local box_w = 320
    local box_h = 56
    local box_x = w//2 - box_w//2
    local box_y = PAD_START_Y - 60

    -- 错误/成功边框
    if self._error_flash > 0 then
        rl.DrawRectangleLinesEx(rl.Rectangle(box_x-2, box_y-2, box_w+4, box_h+4), 3, rl.Color(220, 60, 60, 200))
    elseif self._success_flash > 0 then
        rl.DrawRectangleLinesEx(rl.Rectangle(box_x-2, box_y-2, box_w+4, box_h+4), 3, rl.Color(60, 220, 120, 200))
    end
    rl.DrawRectangleRounded(rl.Rectangle(box_x, box_y, box_w, box_h), 0.1, 8, rl.Color(20, 25, 40, 230))
    rl.DrawRectangleLinesEx(rl.Rectangle(box_x-1, box_y-1, box_w+2, box_h+2), 1, rl.Color(80, 100, 150, 180))

    -- 密码星号显示
    local stars = ""
    for i = 1, MAX_INPUT do
        if i <= #self._input then
            stars = stars .. " ●"
        else
            stars = stars .. " ○"
        end
    end
    local stars_w = rl.MeasureText(stars, 28)
    rl.DrawText(stars, box_x + box_w//2 - stars_w//2, box_y + 12, 28, rl.Color(255, 220, 100, 255))

    -- 数字键盘
    local digits = {"1","2","3","4","5","6","7","8","9"}
    for i, d in ipairs(digits) do
        local row = math.floor((i-1) / GRID_COLS)
        local col = (i-1) % GRID_COLS
        local r = self:_button_rect(row, col)
        self:_draw_button(r, d, rl.Color(35, 45, 70, 240), rl.Color(220, 220, 240, 255))
    end

    -- 退格 ←
    self:_draw_button(self:_button_rect(3, 0), "←", rl.Color(60, 40, 40, 240), rl.Color(240, 150, 150, 255))

    -- 0
    self:_draw_button(self:_button_rect(3, 1), "0", rl.Color(35, 45, 70, 240), rl.Color(220, 220, 240, 255))

    -- 确认 ✓
    self:_draw_button(self:_button_rect(3, 2), "✓", rl.Color(40, 80, 50, 240), rl.Color(150, 240, 170, 255))

    -- 提示文字
    local hint = "点击数字按钮输入密码"
    local hint_w = rl.MeasureText(hint, 18)
    rl.DrawText(hint, w//2 - hint_w//2, PAD_START_Y + 4 * (BTN_SIZE + BTN_GAP) + 16, 18, rl.Color(140, 150, 170, 200))

    -- 错误提示
    if self._error_flash > 0 then
        local err = "✗ 密码错误，请重试"
        rl.DrawText(err, w//2 - rl.MeasureText(err, 22)//2, PAD_START_Y - 140, 22, rl.Color(240, 80, 80, 200))
    end

    -- 成功提示
    if self._success_flash > 0 then
        local ok = "✓ 密码正确！"
        rl.DrawText(ok, w//2 - rl.MeasureText(ok, 26)//2, PAD_START_Y - 140, 26, rl.Color(80, 240, 130, 230))
    end

    Class.call_super(PasswordScene, self, "on_render")
end

function PasswordScene:on_exit()
end

function PasswordScene:on_destroy()
    Class.call_super(PasswordScene, self, "on_destroy")
end

function PasswordScene:_finish_scene()
    if self._finished then return end
    self._finished = true
    if self._execute_next_node then
        self:_execute_next_node()
    end
end

return PasswordScene
