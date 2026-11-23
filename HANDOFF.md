# Aether addons: handoff for a new session

Start every session with:

    git clone <this repo> /home/claude/aether-repo
    cd /home/claude/aether-repo && sh setup.sh

Then read this file. The addons live at the repo root (one folder each);
`tools/` has the tests and art generators; `mock/` has mockup scripts.

## Standing rules (from the user)

- All addon names start with "Aether".
- Deliver the suite as one zip, AetherAddons.zip, built from the repo
  root (`zip -qr9 AetherAddons.zip Aether*`). Never write into the
  user's folders; read access only.
- AetherAddons-README.txt sits at the zip's top level: CRLF line
  endings, lines of 74 characters or fewer (the Win+R command line is
  the one exception and must not change). Update it with every change,
  including the version table.
- Bump the version in each changed addon's .toc and the README table.
- For questions: answer and suggest. Build only after the user says go.
- Bugs: fix and send right away. After a build: test, update the
  README, send the zip.
- Casual, friendly, concise (the user reads on a phone). Oxford comma.
- Check sources before answering factual questions: reliable, multiple
  and independent (not citing each other). Cite them.
- Slow down and think things through.
- Never reproduce Blizzard's class icons; use the original Aether
  glyphs only.
- Mockups: show at actual in-game size (about 1.15 px per UI unit on
  the user's screen; frames at scale 1.17, so about 1.34 px per frame
  unit), plus a zoom. Show before building when asked.
- The user tests in game; ask for screenshots or /af auras output when
  behavior can't be checked here.

## Game facts that matter

- WoW Forever 1.60.1 (interface 16001) carries the Midnight 12.1 addon
  restrictions: in combat, aura data is hidden from addons ("secret"
  values; boolean tests on them error). Aura rows use Blizzard's
  AuraContainer (CustomAuraContainerTemplate). IsMouseOver on those can
  return a secret boolean.
- Pet happiness: C_PetInfo.GetPetHappiness().
- Texture:SetRotation: positive = counter-clockwise.
- TGA art: white with alpha, bottom-left origin (tools/gen_round_art.py
  has write_tga).

## Look (decided)

- Windows: rounded corners (radius 8), blue edge + fine inner line,
  10 px soft glow, navy title strip with gold underline, gold chevrons
  at 12/3/6/9 (26 top/bottom, 34 sides, 3 px out). Docked meter keeps
  only the top chevron. Gold border was shown and NOT chosen (for now).
- XP bar: pill shape; navy earned, bright blue rested, faint gold
  ticks every 5%, gold mark at current XP; chevrons 175% (ends) and
  130% (middle) of bar height, 3 px out.
- Level badges: white number with black outline; "??" is a red ring
  around a black center. Class medallion at 3 o'clock; pet happiness
  face at 3 o'clock on the pet crest, pet level at 6.
- Hub buttons: verb first, Title Case, "..." if it asks first, all with
  the same blue edge (red edge on reset/clear was tried and REJECTED).
  Selected choices: lettering in Aether yellow (SetSelected swaps font
  objects; SetTextColor gets wiped by LockHighlight).

## Open items / waiting on the user

Current build: Frames 1.14.0, Hub 1.13.2, Bars 1.14.0, Chat 1.0.6,
Pack 1.2.1 (others unchanged).

AetherPack 1.2.0 (2026-11-23, built and sent; in-game check pending):
one-bag windows. A plain click on a bag-bar slot (CharacterBag0-3Slot,
CharacterReagentBag0Slot; PreClick/PostClick hooks) or a lone ToggleBag
for bags 1-4 or the reagent bag opens that bag's own window (4 columns,
slot order, name + used/total). Anything else in the same moment (the
bag key, backpack, open/close all, or several ToggleBags at once) goes
to the combined window. Key toggle: combined shown -> close everything;
else open combined. Undragged windows stack from the lower right;
dragged ones save to db.bagPos. Test: tools/pack_bagwin_test.py (run
with no argument and with allviatogglebag).
1.2.1: Blizzard's reagent bag window (bag 5) is now hidden too (it slipped
through IsCarriedBagFrame's 0-4 check); windows widen to fit the bag name.

AetherFrames work of 2026-11-23 (all built and sent; user liked the
result in game videos):
- Centering (1.7.0): once at first login, then /af center. Gap 61 units
  between capsules, pet/tot row 120 lower, inner ends shared, pixel
  snapped. User: AetherHub changes only when they ask.
- Line up after moving (1.8.x): on lock after dragging player/pet/target/
  tot, a box asks Line Up / Line Up and Center / Keep As Is (copy of the
  window trim in AetherFrames/Media/win_*). Player is the anchor; only
  frames within 20 units are pulled in. Hub Layout page has Line Up
  Frames and Line Up and Center Frames (Hub 1.13.2; /af lineup [center]).
  Align Bars does NOT move frames (recommended keeping them separate).
- 3D portraits (1.9.x): PlayerModel at level f-1 (square S/sqrt2), glow
  frame at f-2 (navy CIRCLE disc + portrait_glow.tga), crest{S}_rim over
  the model, f.faceBacking (DARK disc, f-3, never faded).
  tools/gen_portrait_art.py makes the art. WoW Forever's SetUnit returns
  false even on success: only an error, or no model 0.75 s later, falls
  back to 2D. /af portraits 3d|2d|test; /af auras lists each portrait.
  Live tuning: /af portraits zoom|shift [who] (db.portraitTune). The
  user's own numbers: player zoom 1.8 shift 6 2, others zoom 1.3 shift
  0 -2 (saved in their SavedVariables, not defaults yet).
  Known: the model's square shows as straight cuts at the face edge.
- Portrait colors (1.14.0): GlowColor() - enemy mob on target: level
  color (badge's exact color mid, x0.35 rim); players + friendly NPCs on
  target/tot/party: class color, shaded the same way; you (even as your
  own target) and your pet: always Aether blue. /af levelglow, classglow.
- Aggro fading (1.10-1.13): in combat target + tot solid; player/pet/
  party solid only if the target attacks them (UnitIsUnit with
  targettarget, at once) or threat 2-3 against the target. Others fade to
  db.combatAlpha 0.3, bars floor 0.45, faces 0.3 over the dark disc.
  Hidden threat values go through step curves. /af aggro, combatalpha.
- Hit flash (1.11-1.12.4): UNIT_COMBAT WOUND on player/pet/party: red
  halo + crest ring red, hold 0.1 s, fade 0.25 s. /af hits;
  /af hitnumbers (off by default).

Waiting on the user (proposed, not approved):
- Build the portrait numbers in as defaults, plus a thin navy vignette
  to hide the model's straight edges.
- Faded gold accents: solid accents, or a higher /af alpha.
- Hub search box (sidebar top; searches labels and hover text; click a
  result to jump and flash the setting). User liked the idea; mockup
  first.
- XP bar moved ~100 px right sometime before 11:35 (likely a drag while
  Unlock to Move had it unlocked; AetherBars code untouched). Told the
  user how to move or reset it.
- Older: in-game checks of rounded windows, XP bar, button names;
  target debuffs in combat via AuraContainer; level-number nudge.
- Suggested next: shared Aether UI kit (one window trim instead of 9
  copies), cheaper per-frame updates (Coords, Pathfinder minimap pins,
  Frames threat loop, Meter dock polling), Hub pages for Alerts &
  suggestions, Map & minimap, Features, Maintenance; smaller AetherFrames
  art.

## Tests

Run from /home/claude/tools, e.g.:

    for t in hub_general_test frames_test frames_badge_test frames_party_test \
             frames_center_test frames_lineup_test frames_portrait_test \
             frames_aggro_test frames_threat_test frames_aura_test \
             pack_test pack_bagwin_test \
             ledger_full_test bars_xp_test bars_xp_modern_test meter_dock_test \
             chat_test coords_test; do python3 $t.py >/dev/null 2>&1 || echo FAIL $t; done

hub_general_test and ledger_full_test need the user's AetherLedger.lua
SavedVariables at /mnt/user-data/uploads/54619117#1--SavedVariables/.
mock/*.py made today's mockups; several read the user's uploads.
    python3 pack_class_test.py HUNTER

Renderers: frames_render.py (unit frames), decor_render.py (window
trim), xpbar_render.py (XP bar).
