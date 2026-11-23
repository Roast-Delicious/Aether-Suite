from lupa.lua51 import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
table.unpack = table.unpack or unpack
local M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function New() return setmetatable({scripts={}, shown=false}, M) end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.HookScript(s,k,f) local o=s.scripts[k]; s.scripts[k]=function(...) if o then o(...) end f(...) end end
function M.Show(s) s.shown=true; end
function M.Hide(s) local was=s.shown; s.shown=false; if was and s.scripts.OnHide then s.scripts.OnHide(s) end end
function M.IsShown(s) return s.shown end
function M.SetText(s,t) s.text=t end
function M.SetTextColor(s,r,g,b) s.color={r,g,b} end
function M.GetStringHeight() return 12 end
function M.CreateFontString() return New() end
function M.GetOwner(s) return s.owner end
function M.GetRight() return 500 end
FRAMES = {}
CreateFrame = function() local f = New(); FRAMES[#FRAMES+1]=f; return f end
UIParent = New(); function UIParent:GetRight() return 1920 end
GameTooltip = New()
function GameTooltip:SetBagItem(bag, slot) end
function GameTooltip:SetInventoryItem() end
POSTCALLS = {}
TooltipDataProcessor = { AddTooltipPostCall = function(t, fn) POSTCALLS[t] = fn end }
Enum = { TooltipDataType = { Item = 0 } }
hooksecurefunc = function(obj, name, fn) local o=obj[name]; obj[name]=function(...) local r={o(...)}; fn(...); return table.unpack(r) end end
TIMERS = {}
C_Timer = { NewTimer = function(t, fn) local h = {fn=fn, t=t}; function h:Cancel() self.cancelled=true end; TIMERS[#TIMERS+1]=h; return h end }
function RunTimers() for _,h in ipairs(TIMERS) do if not h.cancelled and not h.done then h.done=true; h.fn() end end end
SlashCmdList = {}
UnitName = function() return "Tester" end; GetRealmName = function() return "Forever" end
strsplit = function(sep, str) local o={} for p in string.gmatch(str,"([^"..sep.."]+)") do o[#o+1]=p end return table.unpack(o) end
strlower, strtrim = string.lower, function(s) return (s:gsub("^%s+",""):gsub("%s+$","")) end
geterrorhandler = function() return function(e) print("ERROR", e) end end
GetItemQualityColor = function() return 1,1,1 end
GetCoinTextureString = function(c) return string.format("%dg %ds %dc", math.floor(c/10000), math.floor(c/100)%100, c%100) end
SpellName = nil
C_Spell = { GetSpellName = function(id) return "Recipe#"..id end }
ITEMS = {
  [5000] = { name="Gnoll Paw", class=12, price=0 },
  [5001] = { name="Raptor Hide", class=12, price=0 },
  [2318] = { name="Light Leather", class=7, price=15 },
  [1307] = { name="Gold Pickup Schedule", class=12, price=0 },
}
C_Item = {
  GetItemInfo = function(id) id = tonumber(id) or id; local it = ITEMS[id]; return it.name, nil, 1, nil,nil,nil,nil,nil,nil,nil, it.price end,
  GetItemInfoInstant = function(id) return id,nil,nil,nil,nil, ITEMS[id].class end,
  GetItemCount = function(id, bank) return bank and 12 or 8 end,
}
BAG = {}
C_Container = { GetContainerItemInfo = function(bag, slot) return BAG[bag..":"..slot] end }
LOG = {}
C_QuestLog = {
  GetNumQuestLogEntries = function() return #LOG end,
  GetInfo = function(i) return LOG[i] end,
  GetQuestObjectives = function(id) for _,q in ipairs(LOG) do if q.questID==id then return q.obj end end end,
  IsQuestFlaggedCompleted = function(id) return id == 123 end,
}
GetProfessions = function() return 1 end
GetProfessionInfo = function(i) return "Leatherworking", nil, 60 end
''')
L.execute(open('/home/claude/brand/AetherItemID/AetherItemID_Data.lua').read())
L.execute('AetherItemID_QuestNeeds[5000] = {768}; AetherItemID_QuestNeeds[5001] = {9999}; AetherItemID_QuestNames[9999]="Raptor Thieves"')
L.execute('AetherLensCharDB = { enabled = true, delay = 1.5, known = { ["Tester-Forever"] = { ["Recipe#2160"] = true } } }')
L.execute(open('/home/claude/brand/AetherItemID/AetherItemID.lua').read() + "\nTEST_Describe = Describe", "AetherItemID")
L.execute('''
for _,f in ipairs(FRAMES) do if f.scripts.OnEvent then EV=f end end
EV.scripts.OnEvent(EV, "ADDON_LOADED", "AetherItemID")
function Window() return AetherLensFrame end
function Lines()
  local w = FRAMES[1]  -- the window is the first frame created
  if not w.shown then return "(window hidden)" end
  local out = {}
  for i = 1, 40 do
    local ok = true
  end
  return nil
end
''')
def describe(item, count, bound):
    lines = L.eval(f'TEST_Describe({item}, {count}, nil, {bound})')
    out=[]
    for i in range(1, len(lines)+1):
        t, c, ind = lines[i][1], lines[i][2], (lines[i][3] or 0)
        col = {(1,0.25,0.25):"RED",(1,0.55,0.1):"ORANGE",(0.35,1,0.35):"GREEN",(1,0.82,0):"GOLD",(0.6,0.6,0.6):"GRAY",(1,1,0.35):"YELLOW"}.get((c[1],c[2],c[3]),"")
        out.append("   "+"  "*ind + t + (f"   [{col}]" if col else ""))
    return "\n".join(out)
print("1) Quest item, quest not in log:"); print(describe(5000, 3, "true"))
L.execute('LOG = { {questID=9999, title="Raptor Thieves", obj={ {text="Raptor Hide: 4/10", finished=false} } } }')
print("2) Quest item, quest in log:"); print(describe(5001, 4, "true"))
L.execute('LOG = {}')
print("3) Light Leather, you're a leatherworker:"); print(describe(2318, 20, "false"))
print("4) Item that starts a quest you've done:"); print(describe(1307, 1, "true"))
L.execute('''
BAG["1:5"] = { itemID = 2318, stackCount = 20, isBound = false }
BTN = New(); function BTN:GetBagID() return 1 end; function BTN:GetID() return 5 end
function Refresh() GameTooltip:Hide(); GameTooltip.owner = BTN; GameTooltip:Show(); POSTCALLS[0](GameTooltip) end
TIMERS = {}
Refresh()
for i=1,5 do Refresh() end   -- tooltip refreshes (hide/show) while waiting
''')
win = 'FRAMES[1]'
print("newer bags: timers started =", L.eval('#TIMERS'), "(expect 1)  window before 1s:", L.eval(win+'.shown'))
L.execute('RunTimers()'); print("after 1s: window shown:", L.eval(win+'.shown'))
L.execute('Refresh(); FRAMES[1].scripts.OnUpdate()'); print("tooltip refresh while open: still shown:", L.eval(win+'.shown'))
L.execute('GameTooltip:Hide(); FRAMES[1].scripts.OnUpdate()'); print("moved off the item: window shown:", L.eval(win+'.shown'))
L.execute('TIMERS = {}; Refresh(); GameTooltip:Hide(); RunTimers(); Refresh(); RunTimers()')
print("left before 1s, came back to the same item: opens:", L.eval(win+'.shown'))
L.execute('OUT={}; print=function(s) OUT[#OUT+1]=s end; SlashCmdList.AETHERITEMID("debug"); FRAMES[1]:Hide(); GameTooltip:Hide(); FRAMES[1].scripts.OnUpdate(); TIMERS={}; Refresh(); RunTimers()')
print(L.eval('table.concat(OUT, "\\n")'))
