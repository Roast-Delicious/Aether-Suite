from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
NOW = 100; GetTime = function() return NOW end
SECRET = false; issecretvalue = function(v) return SECRET end
local M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function New() return setmetatable({scripts={}, w=36, shown=true, kids={}}, M) end
function M.SetScript(s,k,f) s.scripts[k]=f end
function M.HookScript(s,k,f) local o=s.scripts[k]; s.scripts[k]=function(...) if o then o(...) end f(...) end end
function M.GetWidth(s) return s.w end
function M.IsVisible(s) return s.shown end
function M.Show(s) s.shown=true end
function M.Hide(s) s.shown=false end
function M.GetFrameLevel() return 3 end
function M.CreateTexture() return New() end
function M.CreateAnimationGroup(s) local g=New(); function g:Play() s.plays=(s.plays or 0)+1 end function g:CreateAnimation() return New() end return g end
CreateFrame = function() return New() end
UIParent = New()
hooksecurefunc = function(obj, name, fn) local o=obj[name]; obj[name]=function(...) local r={o(...)}; fn(...); return table.unpack(r) end end
''')
src = open('/home/claude/brand/AetherBars/AetherBars.lua').read()
start = src.index('-- READY GLOW'); end_ = src.index('local function StyleButton(button)')
L.execute('local db = { readyGlow = true }\nDBREF = db\n' + "--" + src[start:end_] + '\nWatch = WatchCooldown')
L.execute('''
btn = New(); cd = New()
function cd:SetCooldown(s,d) end
function cd:Clear() end
Watch(btn, cd)
function finish() cd.scripts.OnCooldownDone(cd) end
function plays() return btn.aetherGlow and (btn.aetherGlow.plays or 0) or 0 end
''')
def step(label, code):
    L.execute(code); print(label.ljust(52), "glows so far:", L.eval('plays()'))
step("global cooldown 1.5s", 'cd:SetCooldown(NOW,1.5); NOW=NOW+1.5; finish()')
step("real 8s cooldown (re-set mid-way)", 'cd:SetCooldown(NOW,8); NOW=NOW+3; cd:SetCooldown(NOW-3,8); NOW=NOW+5; finish()')
step("cooldown cleared with (0,0), then GCD", 'cd:SetCooldown(NOW,30); NOW=NOW+10; cd:SetCooldown(0,0); cd:SetCooldown(NOW,1.5); NOW=NOW+1.5; finish()')
step("numbers hidden (secret), 10s cooldown", 'SECRET=true; cd:SetCooldown(NOW,10); NOW=NOW+10; finish(); SECRET=false')
step("button hidden when it finishes", 'btn.shown=false; cd:SetCooldown(NOW,10); NOW=NOW+10; finish(); btn.shown=true')
step("glow turned off", 'DBREF.readyGlow=false; cd:SetCooldown(NOW,10); NOW=NOW+10; finish()')
