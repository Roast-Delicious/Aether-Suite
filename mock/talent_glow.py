# The "you can spend a point here" glow in Aether blue (#4DA6FF) at three
# strengths (user, Nov 25 07:07: it read as navy at the soft strength).
import numpy as np, cv2
from PIL import Image, ImageDraw
import talent_states as TS
from talent_details import F, GOLD, BLUE

def glowed(S, strength, spread):
    pad = int(S * 0.35); N = S + 2 * pad
    m = np.zeros((N, N), np.float32)
    cv2.rectangle(m, (pad + 4, pad + 4), (pad + S - 5, pad + S - 5), 1.0, -1)
    g = cv2.GaussianBlur(m, (0, 0), S * spread) * strength
    out = np.zeros((N, N, 4), np.float32); out[..., :3] = BLUE; out[..., 3] = np.clip(g, 0, 1) * 255
    im = Image.fromarray(out.astype(np.uint8))
    t = TS.tile(TS.BOW, border=(140, 175, 215), S=S)
    im.alpha_composite(t, (pad, pad)); return im

W, H = 1040, 470
sheet = Image.new('RGBA', (W, H), (16, 18, 24, 255)); d = ImageDraw.Draw(sheet)
d.text((24, 18), "4  'Can spend a point here' glow, in Aether blue", font=F(28, 'SemiBold'), fill=GOLD)
d.text((24, 60), "Same blue as the frames (#4DA6FF). 2x zoom, then game size.", font=F(17), fill=(170, 176, 188))
for i, (st, sp, name) in enumerate(((0.9, 0.10, "Soft (as before)"), (1.6, 0.13, "Medium  (my pick)"), (2.4, 0.16, "Strong"))):
    x = 30 + i * 340
    d.text((x + 20, 110), name, font=F(18, 'SemiBold'), fill=(235, 238, 245))
    big = glowed(112, st, sp); sm = glowed(64, st, sp)
    sheet.alpha_composite(big, (x, 150)); sheet.alpha_composite(sm, (x + 190, 190))
sheet.convert('RGB').save('/home/claude/aether-repo/mock/out_talent_glow.png'); print(sheet.size)
