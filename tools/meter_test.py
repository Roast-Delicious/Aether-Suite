from lupa import LuaRuntime
lua = LuaRuntime()
lua.execute(r'''
local FIELDS = { Text = true }
local function newObj()
  local o = { shown = true, text = "" }
  return setmetatable(o, { __index = function(self, k)
    if FIELDS[k] then return nil end
    if k == "SetText" then return function(s, v) s.text = v end end
    if k == "GetText" then return function(s) return s.text end end
    if k == "Show" then return function(s) s.shown = true end end
    if k == "Hide" then return function(s) s.shown = false end end
    if k == "IsShown" then return function(s) return s.shown end end
    if k == "SetShown" then return function(s, v) s.shown = v and true or false end end
    if k == "GetHeight" then return function() return HEIGHT end end
    if k == "GetWidth" then return function() return 500 end end
    if k == "GetFrameLevel" then return function() return 1 end end
    if k == "SetScript" then return function(s, ev, fn) s["script_" .. ev] = fn end end
    if k == "CreateFontString" or k == "CreateTexture" then return function() return newObj() end end
    return function() end
  end })
end
HEIGHT = 200
function CreateFrame() return newObj() end
UIParent = newObj(); Enum = {}; RAID_CLASS_COLORS = {}; SlashCmdList = {}; MenuUtil = {}
UNKNOWN = "?"; SHIFT = false
function IsShiftKeyDown() return SHIFT end
function InCombatLockdown() return false end
C_Timer = { NewTicker = function() return { Cancel = function() end } end, After = function() end }
''')
src = open("AetherMeter.lua").read()
src = src.replace("local dpsPanel = CreatePanel", "dpsPanel = CreatePanel", 1)
src = src.replace('local hpsPanel = CreatePanel', 'hpsPanel = CreatePanel', 1)
src += "\nTEST_Update = UpdateRows"
lua.eval("function(s) return load(s, 'AetherMeter.lua') end")(src)("AetherMeter")
print(lua.eval(r'''(function()
  local out = {}
  local p = dpsPanel
  p.visibleRows = 8
  local entries = {}
  for i = 1, 14 do entries[i] = { name = "P" .. i, class = "MAGE", amount = 100 - i, perSecond = 50 - i } end
  local function show(tag)
    local names = {}
    for i = 1, 20 do local r = p.bars[i]; if r.shown then names[#names+1] = r.rankText.text .. r.nameText.text end end
    out[#out+1] = tag .. ": [" .. p.header.text .. "] " .. table.concat(names, " ")
  end
  TEST_Update(p, entries, 49, 1000); show("start          ")
  p.script_OnMouseWheel(p, -1); show("wheel down 1   ")
  for i = 1, 10 do p.script_OnMouseWheel(p, -1) end; show("down 10 more   ")
  p.script_OnMouseWheel(p, 1); show("wheel up 1     ")
  SHIFT = true; p.script_OnMouseWheel(p, 1); SHIFT = false; show("shift+wheel up ")
  p.offset = 5
  TEST_Update(p, { entries[1], entries[2], entries[3] }, 49, 1000); show("only 3 players ")
  return table.concat(out, "\n")
end)()'''))
