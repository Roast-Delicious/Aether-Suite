from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
local M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function New(name) local f=setmetatable({name=name, shown=true, regions={}, pts={}, scripts={}, w=0,h=0}, M); if name then _G[name]=f end; return f end
function M.GetName(s) return s.name end
function M.IsForbidden() return false end
function M.Hide(s) s.shown=false end
function M.Show(s) s.shown=true end
function M.IsShown(s) return s.shown end
function M.SetShown(s,v) s.shown=v and true or false end
function M.GetEffectiveScale() return 1 end
function M.CreateTexture(s) local t=New(); t.tex=true; s.regions[#s.regions+1]=t; return t end
function M.IsObjectType(s,t) return t=="Texture" and s.tex end
function M.GetRegions(s) return unpack(s.regions) end
function M.SetColorTexture(s,r,g,b,a) s.color={r,g,b,a} end
function M.ClearAllPoints(s) s.pts={} end
function M.SetPoint(s,p,rel,rp,x,y) s.pts[#s.pts+1]={p,rel,rp,x,y}; if p=="BOTTOMLEFT" and rel==UIParent then s.l=x; s.b=y end end
function M.SetSize(s,w,h) s.w=w; s.h=h end
function M.SetHeight(s,h) s.h=h end
function M.GetLeft(s) return s.l end
function M.GetBottom(s) return s.b end
function M.GetRight(s) return s.l and s.l+s.w end
function M.GetTop(s) return s.b and s.b+s.h end
function M.IsMouseOver() return false end
function M.HasFocus() return false end
function M.GetFont() return "Fonts\\ARIALN.TTF", 14, "" end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.RegisterEvent() end
hooksecurefunc=function(a,b,c) if type(a)=="string" then local o=_G[a]; _G[a]=function(...) local r=o(...); b(...); return r end else local o=a[b]; a[b]=function(...) local r=o(...); c(...); return r end end end
CreateFrame=function(_,name) local f=New(name); FR=FR or {}; FR[#FR+1]=f; return f end
unpack=table.unpack
UIParent=New("UIParent")
C_Timer={After=function(_,fn) fn() end}
NUM_CHAT_WINDOWS=2
CHAT_FRAME_TEXTURES={"Background","TopLeftTexture"}
for i=1,2 do local cf=New("ChatFrame"..i); cf.l=20; cf.b=200; cf.w=400; cf.h=150
  New("ChatFrame"..i.."Background"); New("ChatFrame"..i.."TopLeftTexture"); New("ChatFrame"..i.."ButtonFrame")
  local tab=New("ChatFrame"..i.."Tab"); tab:CreateTexture(); tab.l=20; tab.b=350; tab.w=60; tab.h=32
  local fs=New(); fs.l=30; fs.w=40; fs.h=12; tab.Text=fs
  local c=cf; tab.GetTop=function() return c.b+c.h+32 end; fs.GetTop=function() return c.b+c.h+16 end
  New("ChatFrame"..i.."EditBox"):CreateTexture()
end
New("ChatFrameMenuButton"); New("ChatFrameChannelButton")
FONTSET={}
FCF_SetChatWindowFontSize=function(_,cf,size) FONTSET[cf.name]=size end
ChatEdit_DeactivateChat=function() end; ChatEdit_ActivateChat=function() end; FCF_Tab_OnClick=function() end
GeneralDockManager={selected=ChatFrame1}
strsplit=function(sep,s,n) local a,b=s:match("^(%S*)%s*(.*)$"); if b=="" then b=nil end; return a,b end
strlower=string.lower; strtrim=function(s) return (s:gsub("^%s+",""):gsub("%s+$","")) end
AetherMeterDB={opacityOutCombat=0.2}; SlashCmdList={}
function AetherBars_PanelRects() return {
  {L=383,R=868,B=270,T=332}, {L=383,R=1072,B=340,T=400}, {L=383,R=1072,B=408,T=478},
  {L=1078,R=1766,B=340,T=400}, {L=1078,R=1896,B=408,T=478} } end
''')
L.execute(open('/home/claude/brand/AetherChat/AetherChat.lua').read().replace("local ADDON = ...","local ADDON = 'AetherChat'"))
L.execute('''
for _,f in ipairs(FR) do if f.scripts.OnEvent then EV=f end end
EV.scripts.OnEvent(EV,"ADDON_LOADED","AetherChat"); EV.scripts.OnEvent(EV,"PLAYER_ENTERING_WORLD")
''')
cf=L.eval('ChatFrame1'); p=L.eval('AetherChatPanel')
print("chat at", cf.l, cf.b, "size", cf.w, cf.h)
print("panel at", p.l, p.b, "size", p.w, p.h, "shown", p.shown)
print("font", L.eval('FONTSET.ChatFrame1'), L.eval('AetherChatDB.fontSize'))
print("bg hidden", not L.eval('ChatFrame1Background').shown, "buttonframe hidden", not L.eval('ChatFrame1ButtonFrame').shown, "menu btn hidden", not L.eval('ChatFrameMenuButton').shown)
print("editbox hidden", not L.eval('ChatFrame1EditBox').shown, "tab underline", L.eval('ChatFrame1Tab').aetherUnder.shown, L.eval('ChatFrame2Tab').aetherUnder.shown)
L.execute('ChatFrameMenuButton:Show()'); print("menu after Blizzard Show", L.eval('ChatFrameMenuButton').shown)
L.execute('SlashCmdList.AETHERCHAT("font 11")'); print("font now", L.eval('FONTSET.ChatFrame1'))
L.execute('SlashCmdList.AETHERCHAT("buttons on")'); print("menu shown", L.eval('ChatFrameMenuButton').shown)
L.execute('ChatFrame1:SetPoint("TOPLEFT", UIParent, "TOPLEFT", 0, 0)'); print("after Blizzard move, chat at", L.eval('ChatFrame1').l, L.eval('ChatFrame1').b)

h = L.eval('ChatFrame1').h
print("COMPACT chat height", h)
assert h == 179.0, h   # 208 panel - 8 inset - 21 (names' top + 5); tall-tab room (34) would give 166   # 13 units more chat than with room up to the tab top (174)
