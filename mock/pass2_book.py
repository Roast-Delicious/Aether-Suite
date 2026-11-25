# Spellbook in the talent tree's scheme (user, Nov 25 07:17):
#  category tabs = gold on navy (like the spec icons); known spells = real
#  art + blue frame (square active, ring passive); trainable now = art +
#  medium blue glow + "Trainer" pill; not yet (level too low) = navy duotone
#  + "Level 42" pill; unavailable = gray. Icons: Blizzard art taken from the
#  user's own talent screenshot, as stand-ins.
import numpy as np, cv2
from PIL import Image, ImageDraw
from skins_lib import Canvas, U, SS, GOLD, BLUE, NAVY, WHITE, DIM, label
from pass2_rep import backdrop
from pass2_friends import searchbox
from pass2_spells import winbtn
from talent_full import icon_at, lum, glow_layer
from talent_details import F

def duo(ic, lo, hi, lift=1.0):
    g = lum(ic); g = (g / max(g.max(), 1e-3))[..., None]
    return lo + g * (hi - lo) * lift
DEEP = np.array([8, 18, 38.]); MID = np.array([60, 100, 160.]); NV = np.array(NAVY, float); GD = np.array(GOLD, float)

# (re-centered on the full screenshot: BM tree half-grid x2)
ICONS = {k: icon_at(*v) for k, v in {
    'bird': (324, 424), 'fire': (414, 424), 'bow': (234, 514), 'fist': (324, 514), 'claw': (414, 514),
    'lion': (234, 604), 'beast': (414, 604), 'green': (324, 604), 'paw': (234, 694), 'eagle': (414, 694),
    'shadow': (504, 694), 'spark': (504, 784), 'mouth': (324, 784), 'tiger': (414, 874)}.items()}

def spell_tile(ic, state, S):
    """S px square (icon + frame). state: known / passive / train / future / off."""
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if state == 'future': a = duo(ic, DEEP, MID, 1.15)
    elif state == 'off':  a = lum(ic)[..., None] * np.array([150, 152, 160.]) * 0.55
    else: a = ic
    i = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((S - 8, S - 8), Image.LANCZOS).convert('RGBA')
    if state == 'passive':
        m = Image.new('L', i.size, 0); ImageDraw.Draw(m).ellipse([0, 0, i.width - 1, i.height - 1], fill=255); i.putalpha(m)
    im.alpha_composite(i, (4, 4))
    col = {'known': BLUE, 'passive': BLUE, 'train': (210, 214, 222), 'future': (60, 90, 140), 'off': (70, 74, 84)}[state]
    if state == 'passive': d.ellipse([2, 2, S - 3, S - 3], outline=col + (255,), width=3)
    else: d.rounded_rectangle([2, 2, S - 3, S - 3], 5, outline=col + (255,), width=3)
    return im

def book():
    W, H = 1240, 860
    c = Canvas(backdrop(W, H))
    box = (40, 46, 40 + 1779, 46 + 1116)
    c.window(box, "", chevrons='l')
    c.text((W - 40, box[1] + 19), "Spellbook", 17, GOLD, 'SemiBold', 'rm')
    winbtn(c, W - 150, box[1] + 19, 'min')
    c.crest((86, 92), 40)
    searchbox(c, (W - 330, 86, W - 40, 120), "Search")
    c.d.line(c.P(62, 152, W, 152), fill=BLUE + (255,), width=SS)
    c.d.line(c.P(640, 170, 640, H), fill=BLUE + (110,), width=SS)
    base = c.done().convert('RGBA'); d = ImageDraw.Draw(base)
    # crest + category tabs: gold on navy, like the spec icons
    def gold_on_navy(ic, S, circle=False):
        g = lum(ic); g = (g / max(g.max(), 1e-3))[..., None]
        a = NV + g * GD * 1.05
        i = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((S, S), Image.LANCZOS).convert('RGBA')
        if circle:
            m = Image.new('L', (S, S), 0); ImageDraw.Draw(m).ellipse([0, 0, S - 1, S - 1], fill=255); i.putalpha(m)
        return i
    base.alpha_composite(gold_on_navy(ICONS['bow'], 70, True), (51, 57))
    d.ellipse([51, 57, 121, 127], outline=BLUE + (255,), width=3)
    for k, (key, act) in enumerate((('bird', True), ('beast', False), ('bow', False), ('claw', False))):
        x = 150 + k * 80
        t = gold_on_navy(ICONS[key], 54); base.alpha_composite(t, (x + 5, 79))
        d.rounded_rectangle([x, 74, x + 64, 138], 7, outline=(GOLD if act else BLUE) + (255,), width=3 if act else 2)
    # pages
    sections = [(70, "General", [("Attack", "", 'known', 'mouth'), ("Berserking", "Racial", 'known', 'fire'),
                                ("Dual Wield", "Passive", 'passive', 'claw'), ("Parry", "Passive", 'passive', 'fist')]),
                (660, "Beast Mastery", [("Aspect of the Hawk", "Rank 5", 'known', 'bird'), ("Mend Pet", "Rank 4", 'known', 'beast'),
                                        ("Mend Pet", "Rank 5", 'train', 'beast'), ("Bestial Wrath", "Talent", 'known', 'green'),
                                        ("Aspect of the Wild", "Level 46", 'future', 'eagle'), ("Beast Lore", "Rank 1", 'known', 'tiger'),
                                        ("Intimidation", "Other spec", 'off', 'shadow'), ("Volley", "Level 40", 'future', 'spark')])]
    S = 60
    for x0, title, spells in sections:
        for i in range(len(spells)):
            x, y = x0 + 20 + (i % 2) * 280, 232 + (i // 2) * 92
            L = Image.new('RGBA', base.size, (0, 0, 0, 0)); ImageDraw.Draw(L).rounded_rectangle([x, y, x + 266, y + 78], 9, fill=NAVY + (140,)); base.alpha_composite(L)
    for x0, title, spells in sections:
        c2 = ImageDraw.Draw(base)
        c2.text((x0 + 20, 178), title, font=F(24, 'SemiBold'), fill=GOLD + (255,))
        c2.line([(x0 + 20, 210), (x0 + 560, 210)], fill=BLUE + (170,), width=2)
        for i, (n, sub, st, key) in enumerate(spells):
            col, row = i % 2, i // 2
            x, y = x0 + 20 + col * 280, 232 + row * 92
            # row backing
            ix, iy = x + 9, y + 9
            if st == 'train':
                gl, pad = glow_layer(S, 2.4, 0.2); base.alpha_composite(gl, (ix - pad, iy - pad))
            base.alpha_composite(spell_tile(ICONS[key], st, S), (ix, iy))
            dd = ImageDraw.Draw(base)
            name_col = {'future': (150, 170, 200), 'off': (120, 124, 134)}.get(st, WHITE)
            dd.text((x + 82, y + (28 if sub else 39)), n, font=F(18, 'SemiBold'), fill=name_col + (255,), anchor='lm')
            if st in ('train', 'future'):
                txt = "Trainer" if st == 'train' else sub; pc = BLUE if st == 'train' else (90, 130, 190)
                f = F(14, 'Bold'); w = dd.textlength(txt, font=f) + 14
                dd.rounded_rectangle([x + 82, y + 46, x + 82 + w, y + 66], 10, fill=(8, 12, 22, 255), outline=pc + (255,), width=2)
                dd.text((x + 82 + w / 2, y + 56), txt, font=f, fill=pc + (255,), anchor='mm')
            elif sub:
                dd.text((x + 82, y + 54), sub, font=F(15), fill=(DIM if st != 'off' else (110, 114, 124)) + (255,), anchor='lm')
    # legend
    lg = ImageDraw.Draw(base); y = 760
    items = [(BLUE, "Known (blue frame; ring = passive)"), ((210, 214, 222), "Trainable now (blue glow)"),
             ((60, 90, 140), "Not yet: level too low (navy)"), ((70, 74, 84), "Unavailable (gray)")]
    for i, (col, t) in enumerate(items):
        x = 70 + (i % 2) * 560; yy = y + (i // 2) * 34
        lg.rounded_rectangle([x, yy, x + 20, yy + 20], 4, outline=col + (255,), width=3)
        lg.text((x + 32, yy + 10), t, font=F(16), fill=WHITE + (255,), anchor='lm')
    return base.convert('RGB')

if __name__ == '__main__':
    im = label(book(), "Spellbook in the talent scheme (game size; icons from your screenshot as stand-ins)")
    im.save('/home/claude/aether-repo/mock/out_p2_book.png'); print(im.size)
