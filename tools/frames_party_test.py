# Party frames, game-drawn aura rows (AuraContainer), and happiness via C_PetInfo.
import re
src=open('frames_test.py').read()
pre=src.split("src=open('/home/claude/brand/AetherFrames")[0]
pre=pre.replace('enemy=true}}','''enemy=true},
       party1={name="Thyme",lvl=35,hp=1762,hpm=1762,pw=1445,pwm=1445,pt=0,tok="MANA"},
       party2={name="Brannoc",lvl=33,hp=1410,hpm=2210,pw=35,pwm=100,pt=1,tok="RAGE"},
       party3={name="Vexmire",lvl=32,hp=1080,hpm=1080,pw=1320,pwm=1320,pt=0,tok="MANA",offline=true}}''',1)
exec(pre)
L.execute(r'''
AURA_CONTAINER_OK=true
CONTAINERS={}
local orig=CreateFrame
CreateFrame=function(kind,name,parent,tmpl)
  local f=orig(kind,name,parent,tmpl)
  if kind=="AuraContainer" then
    f.groups={}
    function f:AddAuraGroup(key,filter,opts)
      self.groups[#self.groups+1]={key=key,filter=filter,opts=opts}
      local b=orig("AuraButton",nil,self)
      opts.initializeFrame(b)      -- the game styles its buttons through this
      self.lastButton=b
    end
    function f:SetUnit(u) self.unit=u end
    function f:UpdateAllAuras() self.updates=(self.updates or 0)+1 end
    function f:SetFlowLayoutAnchorPoint(p) self.anchor=p end
    function f:SetFlowLayoutGrowthDirection(x,y) self.grow={x,y} end
    CONTAINERS[#CONTAINERS+1]=f
  end
  return f
end
UnitIsConnected=function(u) return not (UNITS[u] and UNITS[u].offline) end
UnitInRange=function(u) return u~="party2", true end
UnitClass=function(u) local m={party1="PALADIN",party2="WARRIOR",party3="MAGE"}; local t=m[u] or "HUNTER"; return t,t end
UnitIsPlayer=function(u) return u~="pet" and u~="target" end
GetPetHappiness=nil
getmetatable(UIParent).SetAlphaFromBoolean=function(s,v,a,b) s.alpha = v and a or b end
C_PetInfo={GetPetHappiness=function() return 2 end}
PartyFrame=New("Frame",nil,"PartyFrame"); PartyFrame.shown=true
PartyFrame.GetLeft=function() return 30 end; PartyFrame.GetTop=function() return 700 end
''')
src=open('/home/claude/brand/AetherFrames/AetherFrames.lua').read().replace("local ADDON = ...","local ADDON = 'AetherFrames'")
L.execute(src)
L.execute('''
for _,o in ipairs(ALL) do if o.scripts.OnEvent then EV=o end end
EV.scripts.OnEvent(EV,"ADDON_LOADED","AetherFrames"); EV.scripts.OnEvent(EV,"PLAYER_LOGIN")
for i=1,3 do local f=_G["AetherFramesParty"..i]; f.shown=true; f.scripts.OnShow(f) end
AetherFramesPet.shown=true; AetherFramesTarget.shown=true
EV.scripts.OnEvent(EV,"PLAYER_TARGET_CHANGED")
for i=1,12 do EV.scripts.OnUpdate(EV,0.1) end
''')
ok=True
def check(cond,msg):
    global ok
    print(("ok   " if cond else "FAIL ")+msg); ok=ok and cond
n=L.eval('#CONTAINERS'); check(n==6, "containers made: %d (target, yours, 4 party)"%n)
tc=L.eval('CONTAINERS[1]')
cs=[L.eval('CONTAINERS[%d]'%i) for i in range(1,n+1)]
byunit={c.unit:c for c in cs}
t=byunit.get('target'); check(t is not None and t.groups[1].filter=="HARMFUL" and t.groups[2].filter=="HELPFUL", "target: debuffs first, then buffs")
check(t.anchor=="TOPRIGHT" and t.grow[1]==-1, "target row grows right to left")
check((t.updates or 0)>=1, "target row refreshed on target change")
check(not L.eval('AetherFramesTargetAuras').shown, "old target row hidden")
check(t.shown!=False, "game-drawn target row showing")
b=t.lastButton
check(b.w==24 and any(c.kind=="FontString" for c in b.children.values()), "buttons styled: 24px, with stack and time text")
p1=byunit.get('party1'); check(p1 is not None and p1.groups[1].filter=="HARMFUL" and p1.groups[1].opts.maxFrameCount==4, "party1: up to 4 debuffs")
pl=byunit.get('player'); check(pl is not None and pl.shown==False, "your own row hidden (myBuffs off)")
for i,(name,cls) in enumerate([("Thyme","paladin"),("Brannoc","warrior"),("Vexmire","mage")],1):
    f=L.eval('AetherFramesParty%d'%i)
    check(f.nameFS.text==name, "party%d name %s"%(i,name))
    check(f.classMedal.shown and f.classMedal.glyph.tex.endswith("class_"+cls), "party%d medallion %s"%(i,cls))
    check(f.badge.text.text==str(L.eval('UNITS.party%d.lvl'%i)), "party%d level badge"%i)
    check(f.classMedal.w==17, "party%d medallion sized for the small crest"%i)
f2=L.eval('AetherFramesParty2'); check(abs((f2.alpha or 1)-0.45)<1e-6, "out of range fades to 45%%: %s"%f2.alpha)
f1=L.eval('AetherFramesParty1'); check((f1.alpha or 1)==1, "in range: full")
f3=L.eval('AetherFramesParty3'); check(f3.bars[1].pctFS.text=="Offline", "offline shows Offline: %r"%f3.bars[1].pctFS.text)
check(f3.bars[1].sb.sbc[1]==0.4, "offline bar gray")
check(not L.eval('PartyFrame').shown, "Blizzard party frame hidden")
pos=L.eval('AetherFramesDB.pos.party'); check(pos is not None and pos[1]==30, "party starts where Blizzard's was")
f4=L.eval('AetherFramesParty4'); pt=f4.pts[1]; check(L.eval('function(a,b) return rawequal(a,b) end')(pt[2],L.eval('AetherFramesParty3')) and pt[5]<-50, "party frames stacked: %s"%pt[5])
# happiness via C_PetInfo
bd=L.eval('AetherFramesPet.happyMedal'); check(bd.shown, "happiness badge showing (C_PetInfo)")
lay=bd.layers
check(lay[2][1].alpha==1 and lay[1][1].alpha==0 and lay[3][1].alpha==0, "content face (2) on")
pet=L.eval('AetherFramesPet')
check(pet.badge.text.text=="34", "pet level badge at 6 o'clock: %r"%pet.badge.text.text)
check(all(t.shown==False for t in pet.sideChev.values()), "pet 3 o'clock chevron hidden under the happiness face")
check(pet.happyMedal.w==17, "happiness medallion same size as party class medallions")

# The game-drawn row answers IsMouseOver with a hidden value: must count as "not over", no error.
L.execute(r"""
SM={}; issecretvalue=function(v) return getmetatable(v)==SM end
for _,c in ipairs(CONTAINERS) do c.IsMouseOver=function() return setmetatable({},SM) end; c.IsShown=function() return true end end
AetherFramesTarget.IsMouseOver=function() return false end
AetherFramesTarget.curAlpha=nil
local ok,err=pcall(function() for i=1,3 do EV.scripts.OnUpdate(EV,0.1) end end); OVER_OK=ok; OVER_ERR=tostring(err)
""")
check(L.eval('OVER_OK'), "secret mouse-over from the aura row: no error (%s)"%L.eval('OVER_ERR'))
check(abs(L.eval('AetherFramesTarget.curAlpha')-L.eval('AetherFramesDB.alpha'))<1e-6, "and the target frame still fades out of combat")
print("ALL OK" if ok else "SOME FAILED")
