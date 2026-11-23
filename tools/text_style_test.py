# The AETHER TEXT snippet: Fira fonts made from Blizzard's, world fonts outlined,
# Blizzard's font kept if Fira can't load, and every name the addons use exists.
import re, sys, glob
import lupa.lua51 as l
fails = []
def run(fira_ok):
    L = l.LuaRuntime(unpack_returned_tuples=True)
    L.execute("""
FIRA_OK = %s
local FO = {}; FO.__index = FO
function FO:SetFont(file, size, flags)
  if file:find('FiraSans') and not FIRA_OK then return false end
  self.file, self.size, self.flags = file, size, flags; return true end
function FO:GetFont() return self.file, self.size, self.flags end
function FO:CopyFontObject(o) self.file, self.size, self.flags, self.color = o.file, o.size, o.flags, o.color end
function FO:SetShadowColor(r,g,b,a) self.shadow = a end
function FO:SetShadowOffset(x,y) self.sx = x end
function CreateFont(name) local f = setmetatable({}, FO); _G[name] = f; return f end
local function Base(name, size, color) local f = CreateFont(name); f.file='Fonts\\\\FRIZQT__.TTF'; f.size=size; f.flags=''; f.color=color end
Base('GameFontNormal', 12, 'gold'); Base('GameFontNormalSmall', 10, 'gold'); Base('GameFontNormalLarge', 16, 'gold')
Base('GameFontNormalHuge', 20, 'gold'); Base('GameFontHighlight', 12, 'white'); Base('GameFontHighlightSmall', 10, 'white')
Base('GameFontDisable', 12, 'gray'); Base('GameFontDisableSmall', 10, 'gray')
""" % ("true" if fira_ok else "false"))
    L.execute(open('/home/claude/aether-suite/tools/aether_text.lua').read())
    return L
def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)
L = run(True)
E = L.eval
check("window text: Fira Regular, Blizzard's color", E("AetherFontHighlight.file:find('Regular') ~= nil and AetherFontHighlight.color == 'white'"))
check("gold headings: Fira SemiBold, gold", E("AetherFontNormal.file:find('SemiBold') ~= nil and AetherFontNormal.color == 'gold'"))
check("sizes 5% up for Fira's shorter capitals", abs(E("AetherFontHighlightSmall.size") - 10.5) < 1e-6 and abs(E("AetherFontNormalLarge.size") - 16.8) < 1e-6)
check("window text: soft shadow, no outline", E("AetherFontHighlight.flags") == "" and abs(E("AetherFontHighlight.shadow") - 0.8) < 1e-6)
check("world text: Fira Bold with outline", E("AetherFontWorldSmall.file:find('Bold') ~= nil and AetherFontWorldSmall.flags == 'OUTLINE'"))
check("fonts come from AetherHub", "AddOns\\AetherHub\\Media\\Fonts\\FiraSans-" in E("AetherFontHighlight.file"))
L.execute("AetherFontHighlight.size = 99"); L.execute(open('/home/claude/aether-suite/tools/aether_text.lua').read())
check("a second addon loading it changes nothing", E("AetherFontHighlight.size") == 99)
L = run(False); E = L.eval
check("no Fira file: Blizzard's font and size kept", E("AetherFontHighlight.file") == "Fonts\\FRIZQT__.TTF" and E("AetherFontHighlight.size") == 12)
L = run(True)
used = set()
for p in glob.glob('/home/claude/aether-suite/Aether*/*.lua'):
    s = open(p).read()
    used |= set(re.findall(r'"(AetherFont[A-Za-z]*)"', s))
    # names built by concatenation, e.g. ("AetherFontNormal" or ...) .. "Small"
    for base in re.findall(r'"(AetherFont[A-Za-z]*)"[^\n]*\.\. \(?[^\n]*"Small"', s): used.add(base + "Small")
missing = [n for n in sorted(used) if L.eval(n) is None]
check("every Aether font name used in the addons exists (%d names)" % len(used), not missing)
if missing: print("   missing:", missing)
print("FAILED:", fails) if fails else print("all passed")
sys.exit(1 if fails else 0)
