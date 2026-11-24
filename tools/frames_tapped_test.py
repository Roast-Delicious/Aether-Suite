# A mob tagged by someone else is grayed out on the target frame (name, health
# bar, flat portrait), and goes back to normal when the tag clears.
src = open('frames_test.py').read().split("for name in [")[0]
src = src.replace("SlashCmdList={}\n", "SlashCmdList={}\nfunction M.SetTextColor(s,r,g,b) s.tc={r,g,b} end\nUnitPlayerControlled = function(u) return u ~= 'target' end\nTAPPED = false\nUnitIsTapDenied = function(u) return u == 'target' and TAPPED end\n", 1)
exec(src)
def state():
    L.execute('''local f = AetherFramesTarget
      local function find(o, pred) for _, c in pairs(o.children) do if pred(c) then return c end local r = find(c, pred) if r then return r end end end
      BAR = find(f, function(c) return c.sbc ~= nil end)''')
    t = L.eval('AetherFramesTarget')
    bar = L.eval('BAR.sbc'); 
    return tuple(round(v,2) for v in (bar[1],bar[2],bar[3]))
ok = True
def expect(label, got, want):
    global ok; good = got == want; ok &= good; print(("ok  " if good else "FAIL"), label, got)
L.execute('AetherFramesTarget.shown = true')
expect("untagged: green health bar", state(), (0.18, 0.62, 0.27))
L.execute('TAPPED = true; EV.scripts.OnEvent(EV, "UNIT_FACTION", "target")')
expect("tagged by someone else: gray bar", state(), (0.5, 0.5, 0.5))
L.execute('''NAMEC = nil; for _, o in ipairs(ALL) do if o.kind == "FontString" and o.text == "Bloodfen Raptor" then NAMEC = o.tc end end''')
expect("tagged: gray name", tuple(round(v,2) for v in L.eval('NAMEC').values()), (0.6, 0.6, 0.6))
L.execute('TAPPED = false; EV.scripts.OnEvent(EV, "UNIT_FACTION", "target")')
expect("tag cleared: green bar again", state(), (0.18, 0.62, 0.27))
L.execute('''NAMEC = nil; for _, o in ipairs(ALL) do if o.kind == "FontString" and o.text == "Bloodfen Raptor" then NAMEC = o.tc end end''')
expect("tag cleared: enemy red name again", tuple(round(v,2) for v in L.eval('NAMEC').values()), (1.0, 0.42, 0.42))
print("PASS" if ok else "FAIL"); import sys; sys.exit(0 if ok else 1)
