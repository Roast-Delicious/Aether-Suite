from lupa.lua51 import LuaRuntime
L = LuaRuntime(unpack_returned_tuples=True)
src = open('/home/claude/brand/AetherItemID/AetherItemID.lua').read()
start = src.index('-- Next to the item tooltip, wherever it fits'); end_ = src.index('\n', src.index('window:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", chosen[1], chosen[2])')) + 5
L.execute('''
CURSOR = {0, 0}
GetCursorPosition = function() return CURSOR[1], CURSOR[2] end
UIParent = { GetEffectiveScale = function() return 1 end, GetWidth = function() return SW end, GetHeight = function() return 1080 end }
SW = 1920
TT = { 1500, 1750, 600, 450 }  -- left, right, top, bottom
GameTooltip = { GetLeft = function() return TT[1] end, GetRight = function() return TT[2] end, GetTop = function() return TT[3] end,
  GetBottom = function() return TT[4] end, GetEffectiveScale = function() return 1 end }
window = { w = 308, h = 220 }
function window:GetWidth() return self.w end
function window:GetHeight() return self.h end
function window:ClearAllPoints() end
function window:SetPoint(p, rel, rp, x, y) self.x, self.y = x, y end
''' + src[start:end_] + '''
TestPlace = Place
TestCovers = CoversCursor''')
def run(label, cursor, tt=None, sw=1920):
    L.execute(f'CURSOR = {{{cursor[0]}, {cursor[1]}}}; SW = {sw}')
    if tt: L.execute(f'TT = {{{tt[0]}, {tt[1]}, {tt[2]}, {tt[3]}}}')
    L.execute('TestPlace()')
    x, y = L.eval('window.x'), L.eval('window.y')
    where = "right of tooltip" if x >= (tt or [1500,1750])[1] else "left of tooltip" if x + 308 <= (tt or [1500])[0] else "above/below tooltip"
    print(f"{label:52} window at x={x:.0f}..{x+308:.0f}, y={y-220:.0f}..{y:.0f} ({where}); covers cursor: {L.eval(f'TestCovers({x},{y},308,220)')}")
run("bags at right edge, cursor right of tooltip", (1780, 560))
run("cursor left of tooltip", (1480, 560), tt=(1500, 1750, 600, 450))
run("tooltip mid-screen, cursor just right of it", (1010, 500), tt=(700, 1000, 600, 450))
run("narrow screen: neither side fits", (900, 560), tt=(700, 1000, 600, 450), sw=1300)
