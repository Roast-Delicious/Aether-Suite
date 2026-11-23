from lupa import LuaRuntime
import math
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
local M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
ALL = {}
function New(kind, parent, name)
  local o = setmetatable({kind=kind, parent=parent, name=name, pts={}, shown=true, alpha=1, children={}, scripts={}, attrs={}}, M)
  if parent and parent.children then table.insert(parent.children, o) end
  if name then _G[name]=o end
  ALL[#ALL+1]=o
  return o
end
function M.CreateTexture(s, n, layer, inh, sub) local t=New("Texture", s); t.layer=layer; t.sub=sub or 0; return t end
function M.CreateMaskTexture(s) return New("Mask", s) end
function M.CreateFontString(s, n, layer) local t=New("FontString", s); t.layer=layer; return t end
function M.SetColorTexture(s,r,g,b,a) s.color={r,g,b,a or 1}; s.tex=nil end
function M.SetTexture(s,p) s.tex=p end
-- like WoW: a texture has one alpha; the color's alpha sets it too
function M.SetVertexColor(s,r,g,b,a) s.vc={r,g,b,a or 1}; if a then s.alpha=a end end
function M.SetRotation(s,r) s.rot=r end
function M.SetAlpha(s,a) s.alpha=a end
function M.GetAlpha(s) return s.alpha end
function M.SetSize(s,w,h) s.w=w; s.h=h end
function M.SetWidth(s,w) s.w=w end
function M.SetHeight(s,h) s.h=h end
function M.GetWidth(s) return s.w end
function M.GetHeight(s) return s.h end
function M.ClearAllPoints(s) s.pts={} end
function M.SetPoint(s,p,rel,rp,x,y) s.pts[#s.pts+1]={p,rel,rp,x or 0,y or 0} end
function M.SetAllPoints(s,rel) s.all=rel or s.parent end
function M.Show(s) s.shown=true end
function M.Hide(s) s.shown=false end
function M.SetShown(s,v) s.shown=v and true or false end
function M.IsShown(s) return s.shown end
function M.SetText(s,t) s.text=t end
function M.SetFormattedText(s,f,...) s.text=string.format(f,...) end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.HookScript(s,k,f) s.scripts[k]=f end
function M.SetAttribute(s,k,v) s.attrs[k]=v end
function M.GetFrameLevel() return 1 end
function M.SetParent(s,p) s.parent=p end
function M.IsMouseOver() return false end
function M.IsForbidden() return false end
function M.GetFont() return "Fonts\\FRIZQT__.TTF", 12, "" end
function M.SetFont(s,f,sz,fl) s.font={f,sz,fl} end
function M.SetMinMaxValues(s,a,b) s.min=a; s.max=b end
function M.SetValue(s,v) s.value=v end
function M.SetStatusBarColor(s,r,g,b) s.sbc={r,g,b} end
function M.SetTexCoord(s,...) s.tc={...} end
function M.GetLeft() return 100 end
function M.GetTop() return 700 end
function M.SetMinMaxValues(s,a,b) s.min=a; s.max=b end
function M.SetReverseFill(s,v) s.reverse=v end
function M.GetStatusBarTexture(s) if not s.fillTex then s.fillTex=New("Texture", nil) end return s.fillTex end
function M.AddMaskTexture(s,m) s.mask=m end
CreateFrame=function(kind, name, parent, tmpl) if kind=="AuraContainer" and not AURA_CONTAINER_OK then error("unknown frame type AuraContainer") end local f=New(kind, parent, name); f.template=tmpl; return f end
CreateFont=function(name) return New("Font", nil, name) end
GameFontNormal=New("Font")
UIParent=New("Frame")
InCombatLockdown=function() return false end
RegisterUnitWatch=function(f) f.watched=true end; UnregisterUnitWatch=function(f) f.watched=false end
UNITS={player={name="Jay Iscariot",lvl=34,hp=1458,hpm=1458,pw=1123,pwm=1195,pt=0,tok="MANA"},
       pet={name="Steve",lvl=34,hp=1400,hpm=1512,pw=96,pwm=100,pt=2,tok="FOCUS"},
       target={name="Bloodfen Raptor",lvl=37,hp=612,hpm=1275,pw=0,pwm=0,pt=1,tok="RAGE",enemy=true}}
UnitExists=function(u) return UNITS[u]~=nil end
UnitName=function(u) return UNITS[u].name end
UnitLevel=function(u) return UNITS[u].lvl end
UnitHealth=function(u) return UNITS[u].hp end
UnitHealthMax=function(u) return UNITS[u].hpm end
UnitPower=function(u) return UNITS[u].pw end
UnitPowerMax=function(u) return UNITS[u].pwm end
UnitPowerType=function(u) return UNITS[u].pt, UNITS[u].tok end
UnitIsDeadOrGhost=function() return false end
UnitIsPlayer=function(u) return u~="target" end
UnitIsEnemy=function(a,u) return UNITS[u] and UNITS[u].enemy end
UnitReaction=function(u) return UNITS[u].enemy and 2 or 5 end
UnitClassification=function() return "normal" end
SetPortraitTexture=function(t,u) t.portrait=u end
GetPetHappiness=function() return 3 end
GetTime=function() return 1000 end
C_UnitAuras={GetAuraDataByIndex=function(u,i) local d={{icon=1,applications=0,duration=3600,expirationTime=1900},{icon=2,applications=0,duration=3600,expirationTime=3520},{icon=3,applications=2,duration=10,expirationTime=1008}}; return d[i] end}
PowerBarColor={MANA={r=0,g=0,b=1},FOCUS={r=1,g=0.5,b=0.25}}
PlayerFrame=New("Frame"); TargetFrame=New("Frame"); PetFrame=New("Frame")
strsplit=function(sep,s,n) local a,b=s:match("^(%S*)%s*(.*)$"); if b=="" then b=nil end; return a,b end
strlower=string.lower; strtrim=function(s) return (s:gsub("^%s+",""):gsub("%s+$","")) end
SlashCmdList={}
''')
src=open('/home/claude/brand/AetherFrames/AetherFrames.lua').read().replace("local ADDON = ...","local ADDON = 'AetherFrames'")
L.execute(src)
L.execute('''
for _,o in ipairs(ALL) do if o.scripts.OnEvent then EV=o end end
EV.scripts.OnEvent(EV,"ADDON_LOADED","AetherFrames"); EV.scripts.OnEvent(EV,"PLAYER_LOGIN")
EV.scripts.OnUpdate(EV, 0.2)
''')
for name in ["AetherFramesPlayer","AetherFramesPet","AetherFramesTarget"]:
    f=L.eval(name)
    print(name, "size", round(f.w,1), round(f.h,1), "attrs", dict(f.attrs), "watched", f.watched, "shown", f.shown)
    for c in f.children.values():
        if c.kind=="FontString" and c.text: print("   text:", repr(c.text))
    # also font strings on holders
    for c in f.children.values():
        if c.kind=="Frame":
            for cc in c.children.values():
                pass
print("blizzard hidden:", not L.eval('PlayerFrame').shown, L.eval('PlayerFrame').parent is not None)
print("happiness shown:", L.eval('AetherFramesPet').children)
