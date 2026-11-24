# AetherHub 1.14.3: the minimap button is a navy disc with a blue rim, and sits
# on AetherSkins' ring when that's up. Runs the real code for the button.
import lupa.lua51 as l, sys
src = open('/home/claude/brand/AetherHub/AetherHub.lua').read()
a = src.index("local minimapButton\n"); b = src.index("\n    PlaceMinimapButton()\n    minimapButton:Show()\nend\n", a) + len("\n    PlaceMinimapButton()\n    minimapButton:Show()\nend\n")
chunk = src[a:b]
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
local M = {}
local function new() return setmetatable({ regs = {}, scripts = {}, w = 0, h = 0 }, { __index = function(t, k)
  local v = M[k]; if v then return v end
  if type(k) == "string" and k:match("^%u") then return function() end end end }) end
function M.CreateTexture(s, _, layer) local t = new(); t.layer = layer; s.regs[#s.regs+1] = t; return t end
function M.SetTexture(s, x) s.tex = x end
function M.CreateMaskTexture(s) return new() end
function M.SetBlendMode(s, m) s.blend = m end
function M.SetAlpha(s, a) s.alpha = a end
function M.SetSize(s, w, h) s.w, s.h = w, h end
function M.GetWidth(s) return s.w end
function M.SetPoint(s, ...) s.pt = {...} end
function M.SetScript(s, k, f) s.scripts[k] = f end
function M.IsShown(s) return true end
function M.GetFrameLevel() return 2 end
CreateFrame = function() BTN = new(); return BTN end
Minimap = new(); Minimap.w = 140
hubDB = { minimapAngle = 215 }
GameTooltip = new(); PREFIX = ""
''')
L.execute(chunk + "\nUpdate = UpdateMinimapButton")
L.execute('Update()')
ok = True
def expect(label, got, want):
    global ok
    good = got == want; ok &= good
    print(("ok  " if good else "FAIL"), label, got)
L.execute('DISC, HL, TRK = nil, nil, false; for _, t in ipairs(BTN.regs) do if t.tex and t.tex:find("btn_disc") then if t.layer == "HIGHLIGHT" then HL = t else DISC = t end end; if t.tex and t.tex:find("TrackingBorder") then TRK = true end end')
expect("navy disc button", L.eval('DISC ~= nil and DISC.w'), 27)
expect("soft highlight (no Blizzard yellow)", (L.eval('HL.blend'), L.eval('HL.alpha')), ("ADD", 0.3))
expect("Blizzard's tracking ring gone", L.eval('TRK'), False)
import math
r0 = math.hypot(L.eval('BTN.pt[4]'), L.eval('BTN.pt[5]'))
expect("without AetherSkins: just outside the ring (76)", round(r0, 1), 76.0)
L.execute('AetherSkins_RingActive = true; AetherHub_RefreshMinimapButton()')
r1 = math.hypot(L.eval('BTN.pt[4]'), L.eval('BTN.pt[5]'))
expect("with AetherSkins: on the ring (72.1)", round(r1, 1), 72.1)
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
