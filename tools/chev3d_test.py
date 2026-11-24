# Every gold chevron in the suite uses the 3D bevel art (one baked image per
# direction, lit from the top-right), is never rotated, and isn't tinted
# (its color is in the art). The dark backings may still rotate.
import re, os, sys, glob
BRAND = '/home/claude/brand/'
ok = True
def expect(label, cond):
    global ok; ok &= bool(cond); print(("ok  " if cond else "FAIL"), label)

lua = {f: open(f, encoding='utf-8', errors='replace').read() for f in glob.glob(BRAND + 'Aether*/**/*.lua', recursive=True)}
# no gold chevron loaded from the flat art any more
flat_gold = [f for f, s in lua.items() if re.search(r'win_chev_gold|chev(58|80)_[a-z]+_gold"|_gold"\s*\)|"gold", +GOLD, +6', s)]
expect("no flat gold chevron art loaded anywhere: %s" % [os.path.relpath(f, BRAND) for f in flat_gold], not flat_gold)
# window pattern: gold3d never rotated, white tint
win = [f for f, s in lua.items() if 'chev3d_" .. ({ top = "up"' in s]
expect("all 9 window chevron blocks use chev3d (%d)" % len(win), len(win) == 9)
for f in win:
    s = lua[f]
    expect(os.path.relpath(f, BRAND) + ": gold not rotated, white tint",
           'if not gold3d and c[5] ~= 0' in s and 'gold3d and { 1, 1, 1, 1 } or g[2]' in s)
bars = lua[BRAND + 'AetherBars/AetherBars.lua']
expect("XP bar: gold chevrons chev3d, not rotated", '"chev3d_" .. c[3]' in bars and 'if not gold3d and c[2] ~= 0' in bars)
expect("bar panel chevron: chev3d_up, white", '"chev3d_up"' in bars and '{ "gold", 1, 1, 1, 7 }' in bars)
fr = lua[BRAND + 'AetherFrames/AetherFrames.lua']
expect("frame crests: gold3d art, white, no flip; mirrored swaps left/right",
       '"_gold3d", { 1, 1, 1 }' in fr and 'box, box, false)' in fr and '(dir == "left" and "right")' in fr)
# every texture the code can ask for exists
for addon in ['AetherBars', 'AetherCoords', 'AetherFrames', 'AetherHub', 'AetherItemID', 'AetherLedger', 'AetherMeter', 'AetherPack', 'AetherSkins']:
    miss = [d for d in ('up', 'right', 'down', 'left') if not os.path.exists(BRAND + addon + '/Media/chev3d_%s.tga' % d)]
    expect(addon + ": chev3d art for all four directions", not miss)
miss = [(S, d) for S in (58, 80) for d in ('up', 'right', 'down', 'left') if not os.path.exists(BRAND + 'AetherFrames/Media/chev%d_%s_gold3d.tga' % (S, d))]
expect("AetherFrames: crest chev58/chev80 gold3d art, all directions", not miss)
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
