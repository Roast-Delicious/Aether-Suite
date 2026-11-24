# AetherCoords 1.3.12: the readout under the minimap is a navy pill with a
# fine blue edge. Reuses coords_test.py's mock, adding texture tracking.
import sys, re
src = open('/home/claude/tools/coords_test.py').read()
head = src[:src.index("L.execute(open('/home/claude/brand/AetherCoords/AetherCoords.lua')")]
exec(head)
L.execute(r'''
local M = getmetatable(UIParent)
TEXS = {}
M.CreateTexture = function(s) local t = New(); t.owner = s; TEXS[#TEXS+1] = t; return t end
M.SetTexture = function(s, x) s.tex = x end
M.SetColorTexture = function(s, r, g, b, a) s.tex = "COLOR"; s.cc = {r, g, b, a} end
M.SetVertexColor = function(s, r, g, b, a) s.vc = {r, g, b, a} end
M.SetTexCoord = function(s, ...) s.tc = {...} end
M.SetWidth = function(s, w) s.w = w end
M.SetHeight = function(s, h) s.h = h end
''')
L.execute(open('/home/claude/brand/AetherCoords/AetherCoords.lua').read(), 'AetherCoords')
L.execute('for _,f in ipairs(FRAMES) do if f.scripts.OnEvent then EV = f end end; EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherCoords"); EV.scripts.OnEvent(EV, "PLAYER_LOGIN")')
# the readout: the frame owning pill textures
L.execute('''
for _, t in ipairs(TEXS) do if t.tex and tostring(t.tex):find("pill_cap") then MINI = t.owner end end
CAPS, LINES = 0, 0
for _, t in ipairs(TEXS) do
  if t.owner == MINI then
    if t.tex == "Interface\\\\AddOns\\\\AetherCoords\\\\Media\\\\pill_cap" then CAPS = CAPS + 1 end
    if t.tex == "Interface\\\\AddOns\\\\AetherCoords\\\\Media\\\\pill_capline" then LINES = LINES + 1 end
  end
end
''')
ok = True
def expect(label, got, want):
    global ok
    good = got == want; ok &= good
    print(("ok  " if good else "FAIL"), label, got)
expect("readout found", L.eval('MINI ~= nil'), True)
expect("two navy caps, two blue cap lines", (L.eval('CAPS'), L.eval('LINES')), (2, 2))
expect("old black box hidden", (L.eval('MINI.edge.alpha'), L.eval('MINI.bg.alpha')), (0, 0))
L.execute('MINI:SetValue("62.5, 44.4")')
expect("room for the round ends (50 text + 12 + h/2)", L.eval('MINI.w'), 50 + 12 + 20 / 2)
L.execute('NAVYN = 0; for _, t in ipairs(TEXS) do if t.owner == MINI and t.vc and math.abs(t.vc[1] - 0.075) < 1e-6 then NAVYN = NAVYN + 1 end end')
expect("caps and middle are navy", L.eval('NAVYN'), 3)
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
