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
- NEVER build (no AetherAddons.zip, no new features in the code) until
  the user explicitly says to go ahead and build. Approving a design
  ("I like it", "save it") is not a go-ahead. (Set Nov 24, 2026.)
- Bugs: when you find one, work out the fix and get it ready (on a
  branch, tested), then tell the user it's ready for the next build.
  Don't ship it until they say go.
- After an approved build: test, update the README, send the zip.
- AetherDev.zip (this repo, the handoff kit) is made ONLY at the end of a
  session, when the user says they're opening the next one. Don't send it
  with builds.
- Casual, friendly, concise (the user reads on a phone). Oxford comma.
- Check sources before answering factual questions: reliable, multiple
  and independent (not citing each other). Cite them.
- Slow down and think things through.
- Aether gold (1, 0.69, 0) is the only yellow in the suite (whole suite,
  confirmed Nov 24).
- Never reproduce Blizzard's class icons; use the original Aether
  glyphs only.
- Mockups: show at actual in-game size (about 1.15 px per UI unit on
  the user's screen), plus a zoom.
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
- Hub buttons: verb first, Title Case, "..." if it asks first, faint red
  edge for reset/restore/clear, selected choices in Aether yellow.

## Open items / waiting on the user

- Last delivered build (Nov 24): Pack 1.6.0 (gold capsule, Free slots
  text rows: Bags/Reagent colored, Ammo Warning at half a quiver and a
  pulsing Low at 300, Shards pulsing Low under 3, "Show"/"Show empty" on
  folded headers, vivid green #22e650), Ledger 1.5.15 (directions window
  fits, solid on mouseover), Frames 1.14.4, Coords 1.3.9, ItemID 1.1.3,
  Marks 1.6.13 (Aether gold as the only yellow). Waiting on the user's
  in-game check.
- Green for "good" in AetherPack is #22e650 (user chose F). Other addons
  still use their own greens; not asked to change them.
- Tests needing the user's SavedVariables (hard-coded under
  /mnt/user-data/uploads): hub_general_test, ledger_full_test,
  marks_namekey_test, marks_plates_test. itemid_test*.py fail on old
  code too (mocks lack the window-trim textures): stale, fix when
  working on ItemID. travel_window_test.py checks the directions window.

## Tests

Run from /home/claude/tools, e.g.:

    for t in hub_general_test frames_test frames_badge_test frames_party_test \
             ledger_full_test bars_xp_test bars_xp_modern_test meter_dock_test \
             chat_test coords_test; do python3 $t.py >/dev/null 2>&1 || echo FAIL $t; done
    python3 pack_class_test.py HUNTER

Renderers: frames_render.py (unit frames), decor_render.py (window
trim), xpbar_render.py (XP bar).
