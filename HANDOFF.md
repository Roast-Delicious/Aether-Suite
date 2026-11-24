# Aether addons: handoff for a new session

Start every session with:

    git clone <this repo> /home/claude/aether-repo
    cd /home/claude/aether-repo && sh setup.sh

Then read this file. GitHub: github.com/Roast-Delicious/Aether-Suite
(main). On Nov 24 the GitHub history (last: Pack 1.4.2) was joined to
this one with a keep-ours merge; this tree is the user's real build.
Push with `git -c push.negotiate=true push origin main`. The addons live at the repo root (one folder each);
`tools/` has the tests and art generators; `mock/` has mockup scripts.

## Standing rules (from the user)

- The user plays WoW Forever ONLY, no other WoW version. Answer for
  Forever. Retail/Midnight or Classic sources are background at most:
  say so, and say what still needs checking in Forever.
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
- Mockups: show at actual in-game size, plus a zoom. The user's own
  screenshots measure about 1.5-1.6 px per UI unit (AetherPack window
  408 units = 648 px); build mockups on top of their screenshot when
  possible. Give 3-5 options with a recommendation.
- Ask before guessing: when a report can't be reproduced here, ask for
  a screenshot, a short video (frames via ffmpeg) or debug output
  (/qm debug, /af auras, /ledger tracker).
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

- Last delivered build (Nov 24, afternoon): Coords 1.3.11 (round
  waypoint glow, still the old 1 <-> 0.35 pulse), Pathfinder 1.9.5
  (General Goods pins Aether gold), Ledger 1.6.1 (tracker +/- hover
  white), Frames 1.14.6 (no-aggro fade 20%, bars 35%, one-time
  migration db.fade20), Chat 1.0.8 (compact tab strip measured from
  the tab names' top + 5; tab names Aether gold, others dimmed; typing
  line hidden again via OnShow). Others unchanged: Hub 1.14.2, Bars
  1.14.2, Meter 1.13.8, Marks 1.6.13, Pack 1.6.0, ItemID 1.1.3.
  Tests: chat_compact_test, chat_reshow_test (new).
  CONFIRMED in game (Nov 24, 10:12): Chat, Frames (gold chevrons),
  Coords (round gold glow), Pathfinder, Ledger, quest tracker order and
  look, tapped mobs gray, Pack 1.6.0.
- Waiting on the user: glow steady at the dim level, or a softer pulse?
  (user liked the dim end). Screenshots came in: chevrons and glow are
  Aether gold.
- Built Nov 24 (late morning, after the queue): Ledger 1.7.0. Tooltip
  spot B (new AetherLedger_TooltipSpot.lua, hooks
  GameTooltip_SetDefaultAnchor; right edge 8 units left of the tracker,
  mid-screen; goes on the tracker's right if it has < 240 units of room
  on its left; /ledger tooltip toggles, AetherLedgerDB.tooltipSpot) and
  "Ready for turn-in" in Aether sky blue (115,191,255). Tests:
  tooltip_spot_test (new), tracker_look_test (updated). NOT yet
  confirmed in game.
- Designs in progress, NOT queued: key stats in item tooltips: two tight
  chevrons (chev58_left art) after the stat, pointing back at it, stat
  text Aether gold (mock/stat_gold.py). Still open: A all marked lines
  gold vs B Equip lines stay green; tooltips only or character sheet
  too; per-character stat list in the Hub (class defaults, user ticks).
- Idea: AetherSkins (reskin Blizzard windows/popups). Waiting on which
  windows; mockups first.
- Stale tests (fail on the Nov 24 morning code too): bars_glow_test,
  bars_sidefix_test, ledger_suggest_test, lens_test, meter_login_test,
  meter_test, meter_test2, names_test*, radar_test, tracker_test.
- AetherMarks far names (decided, leave as is): beyond 41 yards (WoW
  Forever's nameplate cap, Rare Radar sets it) there's no nameplate; the
  tiny names are the game's, in reaction colors, and addons can't color,
  move or find them. Mouseover still gives a far mob a unit token, so
  its tooltip and target frame show the right color. Within 41 yards
  quest mobs turn blue (confirmed in two user videos). A speculative
  "odd wording" fix was dropped (tools/marks_wording_test.py keeps it).
- Green for "good" in AetherPack is #22e650 (user chose F). Other addons
  still use their own greens; not asked to change them.
- Tests needing the user's SavedVariables (hard-coded under
  /mnt/user-data/uploads): hub_general_test, ledger_full_test,
  marks_namekey_test, marks_plates_test. itemid_test*.py fail on old
  code too (mocks lack the window-trim textures): stale, fix when
  working on ItemID. New this session: tracker_look_test,
  tracker_sort_test, travel_window_test, frames_tapped_test,
  tooltip_spot_test,
  marks_wording_test.

## Session log

- Nov 24, 2026 (10:37): built Ledger 1.7.0 (tooltip spot B, sky-blue
  turn-in text).
- Nov 24, 2026 (late morning): build confirmed in game; tooltip spot B
  and blue turn-in text queued for the next build.
- Nov 24, 2026 (afternoon): round waypoint glow, gold sweep, frames
  fade 10% more, chat compact strip/gold tabs/typing line. Rule: WoW
  Forever only.
- Nov 24, 2026: gold capsule and Free slots redesign (Pack), Aether gold
  as the only yellow, Ledger directions window fit + mouseover, Aether
  waypoint star, quest tracker restyle and order, tagged mobs gray out.
  Rules added: no building without a go-ahead; bug fixes prepped and
  queued; dev zip only at session end.

## Tests

Run from /home/claude/tools, e.g.:

    for t in hub_general_test frames_test frames_badge_test frames_party_test \
             ledger_full_test bars_xp_test bars_xp_modern_test meter_dock_test \
             chat_test coords_test; do python3 $t.py >/dev/null 2>&1 || echo FAIL $t; done
    python3 pack_class_test.py HUNTER

Renderers: frames_render.py (unit frames), decor_render.py (window
trim), xpbar_render.py (XP bar).
