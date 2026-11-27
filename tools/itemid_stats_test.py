# Key stats in item tooltips (user Nov 27: B = Equip lines keep green;
# tooltips only; class list + per-character ticks in the Hub).
import lupa.lua51 as l
L = l.LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
function wipe(t) for k in pairs(t) do t[k] = nil end return t end
UnitName=function() return "Soup" end; GetRealmName=function() return "Delicious" end
UnitClass=function() return "Hunter","HUNTER",3 end
local function Tex() local t={shown=true}; t.SetTexture=function(s,x) s.tex=x end; t.SetVertexColor=function() end
  t.SetSize=function(s,w,h) s.w=w end; t.ClearAllPoints=function() end; t.SetPoint=function(s,a,b,c,x) s.x=x end
  t.Show=function(s) s.shown=true end; t.Hide=function(s) s.shown=false end; return t end
TIP={ texs={} }
TIP.GetName=function() return "GameTooltip" end
TIP.CreateTexture=function(s) local t=Tex(); s.texs[#s.texs+1]=t; return t end
TIP.HookScript=function() end
LINES={}
function SetLines(list)
  LINES=list; TIP.NumLines=function() return #LINES end
  for i,txt in ipairs(list) do
    local fs={text=txt, color={1,1,1}}
    fs.GetText=function(s) return s.text end; fs.IsShown=function() return true end
    fs.SetTextColor=function(s,r,g,b) s.color={r,g,b} end
    fs.GetFont=function() return "f", 12 end; fs.GetStringWidth=function() return 80 end
    _G["GameTooltipTextLeft"..i]=fs
  end
end
GameTooltip=TIP
''')
L.execute(open('/home/claude/brand/AetherItemID/AetherItemID_Stats.lua').read())
ok=True
def expect(name, got, want):
    global ok
    g = got == want; ok = ok and g
    print(("ok   " if g else "FAIL ") + name + ("" if g else "  got %r want %r" % (got, want)))
def col(i): return tuple(round(x, 2) for x in L.eval('GameTooltipTextLeft%d.color' % i).values())
def shown(): return L.eval('(function() local n=0 for _,t in ipairs(TIP.texs) do if t.shown then n=n+1 end end return n end)()')
L.execute('''SetLines({"Mottled Hide Leggings","Binds when equipped","112 Armor","+8 Agility","+6 Stamina","+3 Intellect",
  "Equip: +16 Attack Power.", '"A strength of spirit."'}); AetherItemID_MarkStats(TIP)''')
expect("hunter: +8 Agility gold", col(4), (1, 0.69, 0))
expect("hunter: +6 Stamina gold", col(5), (1, 0.69, 0))
expect("hunter: +3 Intellect left white (not a hunter stat)", col(6), (1, 1, 1))
expect("Equip line keeps its own color (B)", col(7), (1, 1, 1))
expect("flavor text mentioning a stat: left alone", col(8), (1, 1, 1))
expect("chevrons: 2 per marked line (dark + gold each) x 3 lines", shown(), 12)
L.execute('AetherItemID_Stats.Set("agi", false); SetLines({"X","+8 Agility","+6 Stamina"}); AetherItemID_MarkStats(TIP)')
expect("Agility unticked: not marked", col(2), (1, 1, 1))
expect("...Stamina still marked", col(3), (1, 0.69, 0))
expect("ticks are per character", L.eval('AetherItemIDDB.statPicks["Soup-Delicious"].agi'), False)
L.execute('AetherItemID_Stats.ClassDefaults(); SetLines({"X","+8 Agility"}); AetherItemID_MarkStats(TIP)')
expect("Use My Class's Stats: Agility back", col(2), (1, 0.69, 0))
L.execute('AetherItemID_Stats.SetEnabled(false); SetLines({"X","+8 Agility"}); AetherItemID_MarkStats(TIP)')
expect("switched off: nothing marked, no chevrons", (col(2), shown()), ((1, 1, 1), 0))
print("ALL OK" if ok else "FAILED")
