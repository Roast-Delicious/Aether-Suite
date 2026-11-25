# Release C, mockup 2: Unit Frames page in layout B (chosen 15:12).
# out_hub_frames.png = the window as it opens; out_hub_frames_full.png =
# the same window made tall enough to show the whole page.
import hub_layout as L
from hub_layout import Page, window, tab, GROUPS
import skins_lib as K

def page(p):
    p.title('Unit Frames', 'You, your pet, your target and your party')
    p.band('Frames', 'AetherFrames')
    p.check('Aether frames for you, your pet and your target')
    p.check('Aether party frames')
    p.check('Target of target under the target frame', new=True)
    p.check('Numbers on your pet\'s resource bar', on=False)
    p.slider('Frame size', 0.4, '100%')
    p.buttons(['Line Up Frames', 'Line Up and Center'])
    p.band('Portraits')
    p.choice('Portraits', ['3D', 'Flat'], '3D', new=True)
    p.check('Threat glow around portraits')
    p.check('Class color behind players\' portraits', new=True)
    p.check('Enemy target\'s glow in its level color', new=True)
    p.check('Red flash when hit', ux=0, row_end=False, new=True)
    p.check('Damage numbers', on=False, ux=210, new=True)
    p.band('Fading')
    p.slider('Out of combat', 0.5, '50%')
    p.check('Faces fade too', on=False)
    p.check('In combat, only your target and whoever has aggro stay solid', new=True)
    p.slider('Everyone else in combat', 0.2, '20%', new=True)
    p.band('Buffs')
    p.check('Your target\'s buffs and debuffs under its frame')
    p.check('Your own buffs in your frame', on=False)
    p.gap(4)
    p.buttons(['!Restore AetherFrames Defaults...'])

def render(full):
    if full: L.HU = 830; L.PB = L.HU - 44
    else: L.HU = 525; L.PB = L.HU - 44
    c = K.Canvas(L.background()); window(c, footer_moves=True)
    y = 42
    for name, sub in GROUPS:
        tab(c, y, name, selected=(name == 'Unit Frames'), h=36, sub=sub); y += 39
    p = Page(c); page(p)
    if not full: p.scrollbar(0.47)
    print('page ends at', round(p.y), 'units')
    return c.done()

def bg_tall():
    from PIL import Image, ImageEnhance
    bg = Image.open('/tmp/v4/f_057.png').convert('RGB')
    w, h = int(L.WU * L.U + 2 * L.M), int(L.HU * L.U + 2 * L.M)
    bg = bg.resize((bg.width * 2, bg.height * 2)).crop((1400, 300, 1400 + w, 300 + h))
    return ImageEnhance.Brightness(bg).enhance(0.55)

if __name__ == '__main__':
    render(False).save('out_hub_frames.png')
    L.background = bg_tall
    render(True).save('out_hub_frames_full.png')
