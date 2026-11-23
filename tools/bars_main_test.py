from lupa import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
L.execute(r'''
local M = {}
M.__index = function(t,k) return M[k] or (type(k)=="string" and k:match("^%u") and function() end or nil) end
function New(kind, name, parent)
  local f = setmetatable({kind=kind, name=name, kids={}, regions={}, parent=parent}, M)
  if parent then table.insert(parent.kids, f) end
  return f
end
function M.GetChildren(s) return table.unpack(s.kids) end
function M.GetRegions(s) return table.unpack(s.regions) end
function M.GetObjectType(s) return s.kind end
function M.IsObjectType(s,k) return s.kind == k end
function M.GetParent(s) return s.parent end
function M.GetName(s) return s.name end
function M.Hide(s) s.hidden = true end
function Tex(owner, name) local t = New("Texture", name); table.insert(owner.regions, t); return t end
hooksecurefunc = function() end
UIParent = New("Frame","UIParent")
MainMenuBar = New("Frame","MainMenuBar",UIParent)
local barArt = New("Frame","BarBackgroundFrame",MainMenuBar); DARK = Tex(barArt,"DarkStrip")
local nested = New("Frame","ArtHolder",barArt); DEEP = Tex(nested,"DeepArt")
local btnHolder = New("Frame","ActionBarHolder",MainMenuBar); HOLDERBG = Tex(btnHolder,"HolderBG")
BUTTONS = {}
for i=1,3 do local b = New("CheckButton","ActionButton"..i,btnHolder); BUTTONICON = Tex(b,"Icon"); BUTTONS[i]=b end
local xp = New("StatusBar","MainMenuExpBar",MainMenuBar); XPTEX = Tex(xp,"XPFill")
local bags = New("Frame","BagsFrame",MainMenuBar); BAGBG = Tex(bags,"BagBG"); New("Button","Bag0",bags)
local micro = New("Frame","MicroHolder",MainMenuBar); local inner = New("Frame","MicroInner",micro); MICROBG = Tex(micro,"MicroBG"); New("Button","CharMicro",inner)
''')
src = open('/home/claude/brand/AetherBars/AetherBars.lua').read()
a = src.index('-- Hide a texture for good'); b = src.index('-- Remove every background texture on a bar frame')
c = src.index('local SKIP = '); d = src.index('local function StripOtherBars()')
L.execute('local db = {hideArt=true}\nlocal groups = {}\n' + src[a:b] + src[c:d] + '''
BUTTONS.prefix = "ActionButton"; groups[1] = BUTTONS
StripMainBar()''')
for n in ["DARK","DEEP","HOLDERBG","BUTTONICON","XPTEX","BAGBG","MICROBG"]:
    print(n.ljust(11), "removed" if L.eval(n+'.hidden') else "kept")
