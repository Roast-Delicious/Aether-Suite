from lupa.lua51 import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
FRAMES = {}
local function newObj(name)
  local o = { shown = true, text = "", w = 0, h = 0, name = name, scripts = {} }
  return setmetatable(o, { __index = function(self, k)
    if k == "Text" then return nil end
    if k == "SetText" then return function(s, v) s.text = v end end
    if k == "GetText" then return function(s) return s.text end end
    if k == "Show" then return function(s) s.shown = true end end
    if k == "Hide" then return function(s) s.shown = false end end
    if k == "IsShown" then return function(s) return s.shown end end
    if k == "SetShown" then return function(s, v) s.shown = v and true or false end end
    if k == "SetSize" then return function(s, w, h) s.w, s.h = w, h end end
    if k == "GetHeight" then return function(s) return s.h > 0 and s.h or 200 end end
    if k == "GetWidth" then return function(s) return s.w end end
    if k == "GetLeft" or k == "GetTop" or k == "GetRight" then return function() return 100 end end
    if k == "GetFrameLevel" then return function() return 1 end end
    if k == "SetScript" then return function(s, ev, fn) s.scripts[ev] = fn end end
    if k == "HookScript" then return function(s, ev, fn) s.scripts[ev] = fn end end
    if k == "CreateFontString" or k == "CreateTexture" then return function() return newObj() end end
    if k == "SetParent" then return function(s, p) s.parent = p end end
    return function() end
  end })
end
function CreateFrame(kind, name) local f = newObj(name); FRAMES[#FRAMES+1] = f; if name then _G[name] = f end; return f end
UIParent = newObj("UIParent"); Enum = {}; RAID_CLASS_COLORS = {}; SlashCmdList = {}; MenuUtil = {}
UNKNOWN = "?"
function IsShiftKeyDown() return false end
function InCombatLockdown() return false end
C_Timer = { NewTicker = function() return { Cancel = function() end } end, After = function() end, NewTimer = function() return { Cancel = function() end } end }
OUT = {}; print = function(s) OUT[#OUT+1] = s end
''')
src = open('/home/claude/brand/AetherMeter/AetherMeter.lua').read()
src = src.replace("local dpsPanel = CreatePanel", "dpsPanel = CreatePanel", 1).replace("local hpsPanel = CreatePanel", "hpsPanel = CreatePanel", 1)
src = src.replace("local divider = mainWindow:CreateTexture", "divider = mainWindow:CreateTexture", 1)
src = src.replace("local splitButton = CreateSmallButton", "splitButton = CreateSmallButton", 1)
L.execute(src, 'AetherMeter')
L.execute('for _, f in ipairs(FRAMES) do if f.scripts.OnEvent then EV = f end end; EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherMeter")')
def state(label):
    print("%-36s DPS panel=%-5s HPS panel=%-5s divider=%-5s SPLIT button=%-5s HPS window=%-5s main width=%s" % (label,
      L.eval('dpsPanel.shown'), L.eval('hpsPanel.shown'), L.eval('divider.shown'), L.eval('splitButton.shown'),
      L.eval('AetherMeterHPSFrame.shown'), L.eval('AetherMeterFrame.w')))
state("default (both)")
L.execute('SlashCmdList.AETHERMETER("show hps")'); state("/am show hps")
print("   chat:", L.eval('OUT[#OUT]'), "| saved:", L.eval('AetherMeterDB.metrics'), "| HPS panel placed in:", L.eval('hpsPanel.parent == AetherMeterFrame and "main window" or "other"'))
L.execute('SlashCmdList.AETHERMETER("show dps")'); state("/am show dps")
L.execute('SlashCmdList.AETHERMETER("split")'); state("/am split while DPS only")
L.execute('SlashCmdList.AETHERMETER("show both")'); state("/am show both (split remembered)")
L.execute('SlashCmdList.AETHERMETER("join")'); state("/am join")
L.execute('AetherMeterFrame.shown = false; SlashCmdList.AETHERMETER("show")'); print("plain /am show still shows the meter:", L.eval('AetherMeterFrame.shown'))
L.execute('SlashCmdList.AETHERMETER("show heals")'); print("bad word:", L.eval('OUT[#OUT]'))
