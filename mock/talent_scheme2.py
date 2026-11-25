# User, Nov 25 07:10: locked in Aether blue instead of navy (shown), navy
# for "not taken but available" (no points left to spend), unavailable gray.
import numpy as np
from PIL import Image, ImageDraw
import talent_states as TS
from talent_details import F, GOLD, BLUE
from talent_glow import glowed

DEEP = np.array([8, 18, 38.]); NAVYMID = np.array([60, 100, 160.])
BLUE_LO = np.array([14, 40, 80.]); BLUE_HI = np.array([77, 166, 255.])
def duo(ic, lo, hi, lift=1.0):
    g = TS.lum(ic); g = (g / max(g.max(), 1e-3))[..., None]
    return lo + g * (hi - lo) * lift

def put(sheet, im, x, y): sheet.alpha_composite(im, (x, y))

W, H = 1180, 640
sheet = Image.new('RGBA', (W, H), (16, 18, 24, 255)); d = ImageDraw.Draw(sheet)
d.text((24, 18), "Empty talents: navy for 'not taken', and locked in blue vs gray", font=F(28, 'SemiBold'), fill=GOLD)
d.text((24, 60), "2x zoom, then game size.", font=F(17), fill=(170, 176, 188))
cols = [("Can take\n(points to spend)", lambda S: glowed(S, 1.6, 0.13), True),
        ("Not taken\n(no points left)\nNAVY", lambda S: TS.tile(duo(TS.LION, DEEP, NAVYMID, 1.15), border=(60, 90, 140), S=S), False),
        ("Locked\nBLUE (as asked)", lambda S: TS.tile(duo(TS.LOCK, BLUE_LO, BLUE_HI, 0.9), border=(77, 166, 255), S=S), False),
        ("Locked\nGRAY  (my pick)", lambda S: TS.tile(TS.LOCK, border=(70, 74, 84), fx='gray', dim=0.5, S=S), False)]
for i, (cap, fn, isglow) in enumerate(cols):
    x = 30 + i * 285
    for k, t in enumerate(cap.split("\n")):
        d.text((x, 100 + k * 22), t, font=F(17, 'SemiBold' if k == 0 else 'Regular'),
               fill=(GOLD if t.isupper() or "(" in t and t.split()[0].isupper() else (235, 238, 245)))
    big = fn(112); sm = fn(64)
    off = (big.width - 112) // 2
    put(sheet, big, x - off, 190 - off); put(sheet, sm, x + 150 - (sm.width - 64) // 2, 214 - (sm.width - 64) // 2)
d.line([(24, 350), (W - 24, 350)], fill=(40, 60, 90))
d.text((24, 370), "Why gray for locked:", font=F(19, 'SemiBold'), fill=(235, 238, 245))
for k, t in enumerate(["Blue already means 'has points' (blue frame) and 'spend here' (blue glow).",
                       "A blue locked talent reads as one you're working on, and pulls the eye to",
                       "what you can't take. Gray steps back; navy says 'open, but no points left'.",
                       "So: gold = maxed, blue = in progress or ready, navy = open, gray = out of reach."]):
    d.text((24, 404 + k * 28), t, font=F(17), fill=(170, 176, 188))
sheet.convert('RGB').save('/home/claude/aether-repo/mock/out_talent_scheme2.png'); print(sheet.size)
