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
- BUILT Nov 24, 12:40 (go-ahead 12:33): AetherSkins 1.0.0 (NEW addon;
  user didn't pick AetherSkins vs AetherCoords, so the recommendation,
  AetherSkins, was used), AetherCoords 1.3.12 (minimap readout = navy
  pill, PillLook), AetherHub 1.14.3 (minimap button = navy disc
  btn_disc, sits on the ring at r*1.03 when AetherSkins_RingActive;
  AetherHub_RefreshMinimapButton). NOT yet confirmed in game.
  AetherSkins minimap: art baked from the approved mockup by
  tools/gen_skins_art.py (ring_plain/day/night 512px spanning +-K=1.2821
  map radii, btn_disc, ico_sun (B), ico_moon, pill_cap, pill_capline;
  chevrons copied from Hub). Hides Blizzard's ring (all texture regions
  of Minimap and MinimapBackdrop + MinimapBorder, MinimapCompassTexture,
  MinimapNorthTag); finds Forever's day/night icon BY POSITION (button-
  sized frame within 0.3R of (0.718R, 0.735R), not protected, not
  LibDBIcon/Aether) and hides it (retries at 2 s and 6 s); top bar
  (MinimapCluster.BorderTop or MinimapBorderTop) art hidden, navy pill
  behind it, zone text yellow->gold (hook on SetTextColor), Fira
  SemiBold. Day = C_DateAndTime.IsDayTime() (Forever-only API,
  warcraft.wiki.gg) else realm clock 5:30-21:00 (GAMETIME_DAWN/DUSK).
  Checked every 15 s; change = lit ring + icon fade out 0.8 s, swap, fade
  in 0.8 s. /skins minimap|day|night|auto|debug. Tests:
  skins_minimap_test, coords_pill_test, hub_mmbutton_test (new);
  tools/skins_render.py renders the in-game result. If something is off
  in game, ask for /skins debug output and a screenshot.
- SHIPPED Nov 24, 13:40 (go 13:37): AetherSkins 1.0.1, the day/night
  icon fix (user, 12:46: Forever's own sun still showed beside ours). Forever's
  icon sits at ~57 deg, ~1.04-1.13 map radii (fixed; same spot at 5:52
  and 12:46), not at our 45 deg, so 1.0.0's 0.3R search missed it. New
  search: GameTimeFrame if on the ring, else frames AND textures up to 3
  levels under Minimap/MinimapCluster/MinimapBackdrop, center 20-85 deg
  and 0.8-1.35R, button-sized, closest to (57 deg, 1.08R); zone bar's
  calendar (~1.6R) and the small button under it (~1.5R) excluded.
  /skins debug now lists everything near the ring's top-right. NOT yet
  confirmed in game; if Forever's sun still shows, ask for /skins debug.
- FIX READY on branch fix-zone-pill (AetherSkins 1.0.2): the zone/clock pill
  covered the tracking and calendar buttons. Not shipped yet.
- 3D chevron (accent) mockups (user, 13:59; mock/skin_chevron3d.py):
  A bevel ridge (recommended), B rounded, C chamfered; lit from the
  top-right like the ring; shading only darkens Aether gold or lifts it
  toward the ring's cream. Waiting on the pick (and whether windows get
  it too).
- Next for AetherSkins (approved looks, not built): world map + quest
  log, Reputation, Friends, Progress Track, then more windows in batches.
  Hub tab/toggle for AetherSkins not made yet (slash only).
- Designs in progress, NOT queued: key stats in item tooltips: two tight
  chevrons (chev58_left art) after the stat, pointing back at it, stat
  text Aether gold (mock/stat_gold.py). Still open: A all marked lines
  gold vs B Equip lines stay green; tooltips only or character sheet
  too; per-character stat list in the Hub (class defaults, user ticks).
- AetherSkins (DESIGN, not queued, nothing built): user wants ALL Blizzard
  windows in the Aether look, the world map for sure, and a minimap
  restyle. Mock kit: mock/skins_lib.py, skin_rep.py, skin_more.py,
  skin_minimap.py. CHOSEN (Nov 24, 11:01): windows = style A (Clean:
  tracker-style headers, blue selected band) with B's capsule (pill)
  bars; ONLY the window's four gold chevrons as accents, nothing added
  on the portrait crest or elsewhere (crest = plain navy disc, blue
  rim). Minimap = round blue ring, 3D bevel, 11 px. LIGHT follows the user's
  reference image (11:40; a blue ring lit by a warm light at the top-
  right): mock/skin_minimap.py ring_ref. Gold glows on the INNER wall
  across from the sun (gaussian, ~48 deg), fading back to blue over a
  long arc THROUGH A LIGHT WARM CREAM (255,236,196) like the reference
  (the user found the earlier short step too abrupt); outer edge stays
  blue; soft gold halo just inside the lit wall; small glint on the
  outer edge by the sun (hidden under the sun button at this spot).
  Option 2 adds warm light pooling onto the map. Night: same in white
  with the moon. Plan: blue bevel texture + shine texture (white with
  alpha), SetVertexColor gold or white by realm time (GetGameTime) when
  the sun/moon icon flips (check how Forever's icon decides); change
  over through plain blue, never gold+white mixed. Hex: Aether gold
  #FFB000, Aether blue #4DA6FF, navy #13284A, sky blue #73BFFF.
  The bevel must stay visible under the glow (11:47, 11:49): ridge slopes
  lit from the sun's side, a fine crest line, and the gold ONLY on the
  inner slope, stopping at the crest; the outer slope on the far side
  faces away from the light and stays shaded blue.
  LOOK APPROVED as a mockup (11:51; '/tmp' renders in mock/skin_minimap.py
  ring_ref). Fine-tune in game after the first build. CHOSEN (11:54): option 1,
  light on the ring only, NO light on the map. Ring color (12:04): the HEADER NAVY #13284A (the
  title strip / dark border), not the bright edge blue (that was a
  misread). ring_ref navy=True: lit slope lighter navy, shaded slope
  deeper, crest line; option 2 adds fine Aether-blue lines on both edges
  like the window frame. Gold/white light unchanged. CHOSEN (12:05):
  option 1, plain navy (no edge lines); night version shown.
  Sun/moon icons: user likes the moon stand-in (pale crescent on a navy
  button, mock _moon). Original sun designs in Aether gold (_sun A round
  rays / B pointed rays / C halo ring). CHOSEN: B, as is (user, 12:23).
  World map mockups (11:54, from the user's windowed and
  full-screen screenshots; mock/skin_worldmap.py): Aether window, plain
  crest, zone buttons as navy capsules (current zone gold, blue
  separators, white arrows), map art kept inside a fine rounded blue
  edge, "You:" box as a navy pill, quest log like the tracker (header
  band, navy/gold quest icons, Ready for turn-in sky blue, gold-check
  boxes, difficulty colors kept, yellow -> gold). APPROVED (11:57).
  Other rules
  used: Neutral bars Aether gold, Friendly+ #22e650, Blizzard's yellow UI
  glyphs recolored (white, gold when selected), Fira Sans. Still need a
  world map screenshot. Minimap shape/border/hide-art is still done by
  12.0/12.1 addons (MidnightMap, ClassyMap, BasicMinimap): allowed.
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

- Nov 24, 2026 (13:40): AetherSkins 1.0.1 (Forever's own sun hidden).
- Nov 24, 2026 (12:40): built AetherSkins 1.0.0 (minimap), Coords
  1.3.12, Hub 1.14.3. Window, world map and minimap looks approved.
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
