exec(open('meter_show_test.py').read().split("def state(label):")[0])
L.execute('''
UIParent.GetWidth = function() return 2560 end
function SetPos(f) local old = f.SetPoint end
for _, n in ipairs({"AetherMeterFrame","AetherMeterHPSFrame"}) do
  local f = _G[n]
  f.SetPoint = function(s, p, rel, rp, x, y) s.pt = {p, x, y} end
end
function AetherBars_PanelRects() return { {L=524,R=1210,B=20,T=82}, {L=1216,R=2036,B=20,T=82}, {L=524,R=1210,B=86,T=148}, {L=1216,R=1902,B=86,T=148}, {L=524,R=1010,B=152,T=210} } end
''')
L.execute('AetherMeterDB.split = false; AetherMeterDB.metrics = "both"')
for _ in range(1): L.execute('for _, f in ipairs(FRAMES) do if f.scripts.OnUpdate then f.scripts.OnUpdate(f, 0.6) end end')
m=L.eval('AetherMeterFrame')
print("docked combined: at", list(m.pt.values()), "size", m.w, m.h, "grip shown", m.grip.shown)
L.execute('SlashCmdList.AETHERMETER("split")')
h=L.eval('AetherMeterHPSFrame')
print("docked split: main", list(m.pt.values()), m.w, "| hps", list(h.pt.values()), h.w)
L.execute('SlashCmdList.AETHERMETER("dock off")')
print("undocked: dock", L.eval('AetherMeterDB.dock'), "grip shown", m.grip.shown, "| msg:", L.eval('OUT[#OUT]'))
