from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
NOW = 100; GetTime = function() return NOW end
SECRET = false; NOTSECRET={[19434]=true,[777]=true,[999]=true,[5]=true,[132222]=true,spell=true}; issecretvalue = function(v) return SECRET and not NOTSECRET[v] end
M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function New() return setmetatable({scripts={}, w=36, shown=true, alpha=1}, M) end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.HookScript(s,k,f) local o=s.scripts[k]; s.scripts[k]=function(...) if o then o(...) end f(...) end end
function M.GetWidth(s) return s.w end
function M.IsVisible(s) return s.shown end
function M.Show(s) s.shown=true end
function M.Hide(s) s.shown=false end
function M.SetAlpha(s,a) s.alpha=a end
function M.SetVertexColor(s,r,g,b) s.color={r,g,b} end
function M.GetFrameLevel() return 3 end
function M.CreateTexture() return New() end
function M.CreateAnimationGroup(s) local g=New(); function g:Play() s.plays=(s.plays or 0)+1 end function g:CreateAnimation() return New() end return g end
CreateFrame = function() local f=New(); ALL=ALL or {}; ALL[#ALL+1]=f; return f end
UIParent = New()
hooksecurefunc = function(obj, name, fn) local o=obj[name]; obj[name]=function(...) local r={o(...)}; fn(...); return table.unpack(r) end end
''')
src = open('/home/claude/brand/AetherBars/AetherBars.lua').read()
start = src.index('-- COOLDOWN GLOW'); end_ = src.index('local function StyleButton(button)')
L.execute('GetActionTexture=function(a) return 132222 end; GetActionInfo=function(a) return "spell", 19434 end; M.RegisterUnitEvent=function(s,e,u) s.unitEvent=e end')
L.execute('local db = { readyGlow = true }\nDBREF = db\n--' + src[start:end_] + '\nWatch = WatchCooldown')
L.execute('''
btn = New(); btn.action = 5; cd = New(); function cd:SetCooldown() end; function cd:Clear() end
Watch(btn, cd)
function tick() for _,f in ipairs(ALL) do if f.scripts.OnUpdate then f.scripts.OnUpdate(f, 0.02) end end end
function state()
  tick()
  local g = btn.aetherGlow
  if not g or not g.shown then return "no glow" end
  if g.flaring then return "GREEN FLARE" end
  return string.format("ring r=%.2f g=%.2f b=%.2f alpha=%.2f", g.ring.color[1], g.ring.color[2], g.ring.color[3], g.alpha)
end''')
def at(label, code): L.execute(code); print(label.ljust(44), L.eval('state()'))
at("GCD just started", 'cd:SetCooldown(NOW,1.5)')
at("GCD over", 'NOW=NOW+1.5; cd.scripts.OnCooldownDone(cd)')
at("used: 10s cooldown (GCD call first)", 'cd:SetCooldown(NOW,1.5); cd:SetCooldown(NOW,10)')
at("  2.5s in", 'NOW=NOW+2.5')
at("  5s in", 'NOW=NOW+2.5')
at("  7.5s in", 'NOW=NOW+2.5')
at("  9.9s in", 'NOW=NOW+2.4')
at("  done", 'NOW=NOW+0.1; cd.scripts.OnCooldownDone(cd)')
at("  flare finished", 'btn.aetherGlow.anim.scripts.OnFinished()')
at("hidden numbers: 1s in", 'SECRET=true; cd:SetCooldown(NOW,10); NOW=NOW+1')
at("hidden numbers: 3s in", 'NOW=NOW+2')
at("hidden numbers: done", 'NOW=NOW+7; cd.scripts.OnCooldownDone(cd); SECRET=false')
L.execute('btn.aetherGlow.anim.scripts.OnFinished()')
at("hidden again (learned 10s): 2.5s in", 'SECRET=true; cd:SetCooldown(NOW,10); NOW=NOW+2.5')
at("hidden again: 5s in", 'NOW=NOW+2.5')
at("hidden again: 9.9s in", 'NOW=NOW+4.9')
at("hidden again: done", 'NOW=NOW+0.1; cd.scripts.OnCooldownDone(cd); SECRET=false')
L.execute('btn.aetherGlow.anim.scripts.OnFinished()')
def cast(sid): L.execute('for _,f in ipairs(ALL) do if f.unitEvent=="UNIT_SPELLCAST_SUCCEEDED" then f.scripts.OnEvent(f,"UNIT_SPELLCAST_SUCCEEDED","player","x",%d) end end' % sid)
print("-- hidden, YOUR cast of this button's spell (learned 10s): no 2s wait")
cast(19434); at("own cast: 0.3s in", 'SECRET=true; cd:SetCooldown(NOW,10); NOW=NOW+0.3')
at("own cast: 1.5s in", 'NOW=NOW+1.2')
at("own cast: 4s in", 'NOW=NOW+2.5')
at("own cast: 7s in", 'NOW=NOW+3')
at("own cast: done", 'NOW=NOW+3; cd.scripts.OnCooldownDone(cd); SECRET=false')
L.execute('btn.aetherGlow.anim.scripts.OnFinished()')
print("-- hidden, ANOTHER spell cast (global cooldown on this button): stays quiet")
cast(999); at("other cast: 0.5s in", 'SECRET=true; cd:SetCooldown(NOW,1.5); NOW=NOW+0.5')
at("other cast: GCD over", 'NOW=NOW+1; cd.scripts.OnCooldownDone(cd); SECRET=false')
print("   learned still:", L.eval('(function() for k,v in pairs(DBREF.cdLearned) do return v end end)()'))
print("-- a spell with only the global cooldown, first use: brief orange, then learned")
L.execute('DBREF.cdLearned={}; GetActionInfo=function(a) return "spell", 777 end')
cast(777); at("gcd-only own cast: 0.5s in", 'SECRET=true; cd:SetCooldown(NOW,1.5); NOW=NOW+0.5')
at("gcd-only: over", 'NOW=NOW+1; cd.scripts.OnCooldownDone(cd)')
cast(777); at("gcd-only again: 0.5s in", 'cd:SetCooldown(NOW,1.5); NOW=NOW+0.5')
at("gcd-only again: over", 'NOW=NOW+1; cd.scripts.OnCooldownDone(cd); SECRET=false')
L.execute('GetActionInfo=function(a) return "spell", 19434 end')
at("cooldown reset early", 'cd:SetCooldown(NOW,30); NOW=NOW+5; cd:SetCooldown(0,0)')
at("bar hidden mid-cooldown", 'cd:SetCooldown(NOW,30); NOW=NOW+5; btn.shown=false')
at("bar shown again", 'btn.shown=true')
at("option off", 'DBREF.readyGlow=false')
