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
- Before any recommendation or diagnosis, check it against everything
  QUEUED FOR THE NEXT BUILD (and any unshipped branch), and say how the
  queue affects it. (User, Nov 24 14:42.)
- At session start, look for OTHER Aether chats (recent_chats) updated
  after this repo's last commit, and read them: decisions made there are
  not in this kit. (Nov 24: a parallel chat's minimap picks were missed.)
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

- LAST BUILD (Nov 25, 03:45; user 03:11: "go ahead with the entire
  interface", with screenshots of Reputation, Progress Track, Talents,
  Friends): AetherSkins 1.2.0 + Hub 1.14.6.
  * NEW AetherSkins_Windows.lua: one generic skinner for every window on
    Blizzard's portrait-window templates (wow-ui-source 12.1.5, keys
    NineSlice/Bg/TopTileStreaks/TitleContainer.TitleText/PortraitContainer
    .portrait/CloseButton/Inset). Approved style A: rounded panel, blue
    edge+inner line, glow, navy title strip + gold underline, gold title
    (AetherSkinsFontTitle), 3D chevrons, navy crest disc (btn_disc) behind
    the portrait, navy close box with white x. Inside (walk, depth 10):
    panel buttons (Left/Middle/Right) navy + white font objects; check
    boxes dark + gold check (desaturate + vertex); MinimalScrollBar blue;
    PanelTabButtonTemplate tabs navy, gold edge when LeftActive shown
    (hooks PanelTemplates_SelectTab/DeselectTab/UpdateTabs); search boxes
    dark; insets faint. Blizzard art only SetAlpha(0); no fields written
    to Blizzard frames (weak tables); in combat -> after PLAYER_REGEN.
    Found by: W.KNOWN names (+ rescan on Blizzard_ ADDON_LOADED) and
    hooksecurefunc ShowUIPanel; /skins this styles the window under the
    mouse. Blizzard yellow font objects (1,.82,0) -> Aether gold
    (W.GoldText, pairs(_G) once at login; Aether* fonts skipped).
    /skins windows on|off (AetherSkinsDB.windows), Hub switch.
    Test: skins_windows_test (35 checks, mock from template keys).
  * NOT YET in game. Expect rough edges: Forever's custom windows
    (Talents, Progress Track side tabs), side tabs in general, rep bars
    (approved capsule bars, Neutral gold / Friendly+ #22e650), rows and
    section headers (tracker-style), world map specifics: phase 2, from
    the user's screenshots + /skins debug.
- READY, NOT SHIPPED (branch fix-handin-unknown-zone) also has AetherSkins
  1.2.2: /skins tree hit its 400-line cap before the open page (65 lines of
  our own pieces, 99 hidden gamepad hints etc.): now skips our textures
  (W.ours), folds hidden parts into one line, cap 1500, depth 7. Reputation
  is a page of CharacterFrame, so its dump is named CharacterFrame.
- READY, NOT SHIPPED (branch fix-handin-unknown-zone): AetherLedger 1.8.2.
  Checklist 5.9/5.10 fail (06:08): "Lost Shipping Crate" [38] (Forever-only
  quest, hand-in Powderfuse Port, the Riverglades: NOT in our data) was
  treated as handed in where it came from (ZonesOf falls back to the log
  header), so no bottom spot, no zone, no divider. Fix: TurnInOf(q) asks
  C_QuestLog.GetNextWaypoint(questID) for finished quests first, our data
  second; used in Fits, the hand-in list and /ledger tracker.
  tracker_handin_test (+2). Delivery quests show Blizzard's description
  (it names the place) instead of "Ready for turn-in", so no zone suffix
  there; the divider still marks them.
- CHECKLIST RESULTS (Nov 25 06:13): 5.1-5.7 pass (errors fixed, Check
  Zones), 5.8 not tested, 5.9/5.10 fail (above), 5.11/5.12 can't test (no
  finished-here or red quests; "Can't test now" option added to the doc's
  Result list), 5.13 pass, 5.14 partial (only CharacterFrame dumped:
  saved tools/dumps/CharacterFrame_2026-11-25.txt; need Reputation,
  Friends, Talents, Progress Track), 5.15 pass (tools/dumps/FullReport_
  2026-11-25.txt; memory 10.2 MB, Coords 81 KB, Pathfinder 1.58 MB).
  Character dump: stat headers atlas UI-Character-Info-Title, rows
  UI-Character-Info-Line-Bounce2, CharacterFrameRightPaneHost StoneBg
  UI-Character-Info-Stat-StoneBG3, CharacterStatsPaneScrollBox .Border
  common-insideframe + .ClassBackground UI-Character-Info-Hunter-BG, side
  tabs CharacterFrameModeTab1-6 (.TabGlow common-sidetab-selected), scroll
  bar IS MinimalScrollBar (styled; tint just too faint).
  Second dump (Reputation open, 06:21, tools/dumps/CharacterFrame_
  ReputationOpen_2026-11-25.txt) also cut at 400 before ReputationFrame,
  but adds: CharacterFrameLeftPaneHost bg atlas UI-Character-Info-General-
  BG, CharacterFrameRightPaneHost bg UI-Character-Info-Stat-BG + divider
  common-framedivider, side tabs CharacterFrameModeTab1-6 = .Background
  common-sidetab, .SelectedTexture/.TabGlow common-sidetab-selected,
  .HighlightTexture common-sidetab-hover, .Icon (Tab1 = RTPortrait1);
  CharacterFrameRightPaneToggleButton (tex 130869/130868/130757);
  CharacterStatsPane categories .ItemLevelCategory/.AttributesCategory/
  .EnhancementsCategory (UI-Character-Info-Title), .ItemLevelFrame
  UI-Character-Info-ItemLevel-Bounce. Need the 1.2.2 dump for the
  Reputation page itself.
  Friends dump (06:22, tools/dumps/SocialUIFrame_2026-11-25.txt, cut at
  400): Forever's Friends window is SocialUIFrame (added to W.KNOWN on
  branch). Parts: .TopFade friends-frame-topTexBG, .BottomFade friends-
  frame-bottomTexBG, BattleNetBar .Background friends-frame-infoBG,
  status dropdown common-dropdown-textholder + common-dropdown-a-button,
  menu button common-button-tertiary-square-normal/pressed + friends-
  icon-menu, filter dropdown common-dropdown-b-button, search box
  common-searchbar-a + common-searchbar-icon-a + common-search-
  clearbutton, list dividers perks-divider-short, broadcast and notice
  popups use UI-Frame-DiamondMetal-* borders. Nested IgnoreListFrame is
  its own PortraitFrame: its close button was NOT styled -> skin nested
  portrait frames too. Tabs, the friends list rows: still need 1.2.2.
  Talents dump (06:24, tools/dumps/PlayerSpellsFrame_Talents_2026-11-25
  .txt, cut at 400 inside the nodes): PlayerSpellsFrame 1218x708, tabs
  at .tabSystem (uiframe-tab-*/uiframe-activetab-*, already styled).
  NOT styled: .MaximizeMinimizeButton (RedButton-Expand/-Condense) ->
  needs our navy box like the close button. TalentsFrame art:
  .Background Talents-Background-c60, class art talent-background-
  hunter (+BackgroundFlash, Overlay*), .BackgroundBorder Talents-inner-
  frame-c60 (bronze), dividers Talents-divider-left/right/vertical-c60,
  clouds/particles animations. Nodes: StateBorder atlases talents-node-
  square-gray/-yellow/-locked, green glow talents-node-square-
  greenglow, sheen talents-sheen-node. Plan: keep class art + nodes
  (game info), restyle bronze border/dividers blue, decide on the
  yellow node border (Blizzard's "has points" color) vs Aether gold.
  Each node is ~23 lines, so 1.2.2 should fold node insides.
  REPUTATION FULL (06:29, 1.2.2, tools/dumps/Reputation_full_2026-11-25
  .txt, 333 lines, complete): ReputationFrame.ScrollBox rows. Headers:
  Button 343x28, two textures common-button-list-collapseExpand (the
  brown bar) + .StateIcon common-button-list-minus/plus + .Name ->
  tracker-style header (navy strip, gold text, white +/-). Faction
  rows: .Content.Name, .Content.ReputationBar (bg common-stat-bar-BG
  160x29, .Fill common-stat-bar-white tinted by standing via vertex
  color, .Mask, .Text) -> capsule bar: our dark track + rounded fill,
  keep the standing color; .Content.BackgroundHighlight .Left/.Middle/
  .Right charactercreate-customize-dropdown-linemouseover-* -> blue
  selected/hover row. ScrollBox has two UI-Character-Info-ScrollLine-
  Long lines (top/bottom) -> blue line. ScrollBar styled (tint too
  faint). .ReputationDetailFrame: .Title, .Subtitle, .Divider UI-
  Character-Info-ScrollLine, .StandingBar (same bar parts, 180x29),
  checkboxes checkbox-minimal (styled), .ViewRenownButton (styled).
  .filterDropdown hidden here. Sibling pages SkillsFrame, PVPRankFrame,
  StatisticsFrame, TokenFrame: need dumps when open (tabs 3-6).
  FRIENDS FULL (06:30, tools/dumps/SocialUIFrame_full_2026-11-25.txt,
  174 lines, complete): .FriendsList: .TopDivider/.BottomDivider perks-
  divider-short -> blue line; .FilterBar dropdown common-dropdown-b-
  button, .SearchBar common-searchbar-a (+icon) -> our input box;
  .ActionButton ("Add Friend") is 128-RedButton-Left/Right/_Center:
  marked [styled button] but its red art is atlas parts .Left/.Right/
  .Center, NOT faded -> fade those. Group headers: Button 365x24 with
  common-button-list-collapseExpand x2 + .CollapseButton (common-button-
  list-minus) + .ButtonText -> navy strip, gold text (same as rep).
  Friend cards 365x70: .Background friends-card-battleNet / friends-
  card-disabled (offline) -> dark navy card, rounded, dimmer offline;
  selected overlay friends-card-selected -> blue; .FriendName, .Location;
  .PresenceHolder.PresenceIcon friends-status-online/offline (keep);
  .PartyButton common-button-tertiary-square-* (+ BattleNetMenuButton
  same) -> small navy icon button. .BattleNetBar .Background friends-
  frame-infoBG + .ControlsContainer.BattleNetBackground (tex 632259) ->
  navy strip; status dropdown common-dropdown-textholder/-a-button.
  .TopFade/.BottomFade friends-frame-top/bottomTexBG -> fade. Side tabs
  (4 unnamed Buttons, common-sidetab*, icons friends-icon-tab-*): same
  treatment as Character side tabs. Hidden pages to dump later: Recent
  Allies, Friend Requests, Raid, Ignore List.
  TALENTS FULL (06:30, tools/dumps/PlayerSpellsFrame_Talents_full_2026-
  11-25.txt, 1241 lines, complete, under the 1500 cap). Nodes (~50,
  20 lines each) under .TalentsFrame.ButtonsParent: .StateBorder states
  seen: -yellow (maxed), -green (has points, not maxed), -gray
  (available, 0 points), -locked. Arrows: Frame with .Line + .ArrowHead
  talents-arrow-head-locked/-gray/-yellow. Plan: yellow border/arrow ->
  tint Aether gold (SetVertexColor on .StateBorder/.ArrowHead after
  Blizzard sets the atlas; hook the node's state update), keep green,
  gray, locked. Spec headers: three Frames 48x48 with .MainRing
  Talents-Main-Ring-c60 + .TextBackground Talents-Main-Ring-Box-c60 +
  .Divider Talents-small-divider-c60 (bronze) -> navy ring + blue
  divider. .ClassCurrencyDisplay .Border Talents-Square-Box-c60
  ("unspent") -> navy box. .SearchBox [styled input] but its bronze
  .Left/.Right/.Middle common-search-border-* NOT faded -> fade.
  .SearchOptionsDropdown .Arrow common-dropdown-a-button -> navy.
  .ApplyButton tex 130824 (styled). TabSystem now 2 tabs (styled).
  Window chrome: .BackgroundBorder Talents-inner-frame-c60, dividers
  Talents-divider-left/right/vertical-c60 -> blue. Keep class art and
  cloud/particle animation (decide with user if too busy). SpellBook is
  .SpellBookFrame (hidden here) -> dump #6 with the Spellbook tab open.
  PROGRESS TRACK = LegacySystemFrame (title "Progress Track"; portrait
  atlas Legacy-up-c60). Dump 06:32, tools/dumps/LegacySystemFrame_
  Rewards_2026-11-25.txt, complete. Added to W.KNOWN (branch skins-
  second-pass). Side tabs .LegacyRewardTrackTab / .LegacyChallengeTab /
  .LegacyTreeTab (common-sidetab*). .RewardTrackPage: .Background
  Legacy-Rewards-Tracker-background (big art), .Icon Legacy-Rewards-
  Tracker-Icon, .Points/.PointsLabel, .ProgressBarBackground Legacy-
  Progressbar-BG + StatusBar .LegacyRewardProgressBar (.ProgressBarFrame
  Legacy-Progressbar-Frame, fill Legacy-Progressbar-Fill) -> capsule
  bar, gold fill. Reward cards (216x241) under .LegacyRewardProgressFrame
  .ClipFrame: .RewardCardBG Legacy-Rewards-Tracker-Cards-Disable (and
  presumably -Cards for earned), .LevelSquare Legacy-Rewards-Tracker-
  Diamond-Disable, .IconBorder Legacy-Rewards-Tracker-Icons-Frame-
  Disable, .EarnedCheckmark worldquest-tracker-checkmark, .Level,
  .RewardName -> navy rounded cards, blue icon frame, gold level badge
  when earned. Arrow buttons .LeftButton/.RightButton/.Jump* hidden
  (only shown with more cards). Hidden pages: .ChallengesPage, .TreePage
  -> dump with those side tabs open. How to open: user found it (ask
  how, for the README/checklist 1.14).
  USER REQUEST (06:33): when reskinning, role-selection icons (tank,
  healer, damage: Group Finder / role check) become FLAT GOLD (#FFB000)
  ON BLUE. Mockup AFTER all the remaining dumps are in.
  CHOSEN (06:48): option A, navy disc + blue ring, gold ring when
  selected, gold check, dim gold when unavailable (mock/roles.py).
  SECOND-PASS MOCKUPS (mock/pass2_*.py, out_p2_*.png): 1 Reputation
  (side tabs navy, selected = gold edge + gold notch; header strips;
  capsule bars; blue selected row w/ gold left accent; stronger blue
  scroll thumb; detail pane) APPROVED 06:50 "love it". 2 Friends (navy
  cards, offline dimmer, selected blue edge; search box; dropdowns;
  small navy icon buttons; navy Add Friend) APPROVED 06:50.
  TALENT ICONS (user 07:00, mock/talent_tint.py): spec header icons
  (Beast Mastery etc.) = C, gold on navy (navy disc + desaturated icon,
  SetBlendMode ADD, vertex gold). Tree nodes: Blizzard art; MAXED =
  gold tint (B: SetDesaturated + SetVertexColor gold) + gold border;
  SOME POINTS = blue border (was green); UNAVAILABLE = gray, as is.
  Open (asked 07:00): 'can take' (0 points, unlocked) vs locked look;
  arrows; count text color; green 'can learn' glow -> blue?
  07:03-07:07: arrows YES, thicker + 3D bevel like the accents (mock/
  talent_details.py), gold/blue/gray by source state. Counts: user wants
  "2 of 5" wording (mock/talent_counts.py: 3b badge, 3c pill on icon,
  3d line under) - pick pending. 1: user leaning 1C with locked in navy
  (mock/talent_1c.py, three strengths) - pick pending. Glow: Aether
  blue #4DA6FF (mock/talent_glow.py, soft/medium/strong) - pick pending;
  user said "Aether looks good" (07:07).
  07:08: counts = 3c, pill CENTERED ON THE FRAME'S BOTTOM EDGE ("2 of 5",
  gold maxed / blue partial). Full-window mockup: mock/talent_full.py
  (on the user's screenshot; unspent shown as 2).
  07:10: glow = MEDIUM Aether blue (talent_glow.py strength 1.6, spread
  .13). User idea 07:10: navy for 'not taken, no points left', locked
  gray; asked for blue-locked mock (talent_scheme2.py). Recommended:
  can take = art + blue glow; not taken = navy duotone; locked = gray.
  CHOSEN 07:16: A (mock/talent_full.py UNSPENT=0 LOCKED=gray): can take
  = art + medium blue glow; not taken (no points) = navy duotone (deep
  #081226 -> #3C64A0, border #3C5A8C); locked = gray (lum x 0.55, border
  #464A54), arrows into locked gray. TALENT DESIGN SETTLED.
  07:17: user "go ahead with the mockups" = mockups 3-5 OK (not a build
  go); Spellbook to follow the talent scheme -> new mock (pass2_book.py).
  07:19: Spellbook talent-scheme mock APPROVED ("love it"). ALL
  SECOND-PASS MOCKUPS APPROVED. Waiting for the build go.
  07:26: AetherPack 1.6.2 into the next build (user OK): hide Blizzard's
  quickslot NormalTexture (130841, the light-gray rounded edge around
  every bag slot, seen in the 07:22 screenshot) and draw a thin Aether
  blue icon frame like the Vendor/Spellbook; quality borders stay on top.
  GROUP FINDER = LFGListingFrame (I). Dump 06:35, tools/dumps/
  LFGListingFrame_2026-11-25.txt, complete. NOT SKINNED AT ALL in game
  (no [styled] marks anywhere): the skinner never caught it -> added
  to W.KNOWN; check why the ShowUIPanel hook missed it (likely shown
  with :Show() directly) -> also hook its OnShow. No close button in the
  dump. Parts: .RolesSection LFGListingFrameRoleBackground groupfinder-
  roles-background; .Inset .CustomBG groupfinder-background, .Border
  common-insideframe; .DividerFrame.Divider common-framedivider; Back /
  Post buttons UIPanelButton tex 130824. Role buttons under
  LFGListingFrameSoloRoleButtons (and hidden ...GroupRoleButtons):
  RoleButtonTank/Healer/DPS: *Background UI-LFG-RoleIcon-<role>-
  Background, icon UI-LFG-RoleIcon-<role> (85x85, unnamed), .cover tex
  337499 (dim when unavailable), .CheckButton old UI-CheckBox (tex
  130750-130755). NewPlayerFriendlyButton: UI-LFG-RoleIcon-Leader +
  newplayerchat-chaticon-newcomer. -> USER REQUEST: flat gold glyphs on
  a blue disc (our own art, Media/role_tank/healer/dps/leader), gold
  check. Category buttons (418x67) under LFGListingFrameCategoryView:
  .Icon groupfinder-button-dungeons/-questing/-battlegrounds/-custom-
  pve (picture banners, keep), .Cover groupfinder-button-cover (+-down,
  -hover) -> navy rounded frame, blue hover, .Label. Hidden views:
  ActivityView, LockedView -> dump after clicking a category.
  SPELLBOOK = PlayerSpellsFrame.SpellBookFrame (dump 06:35, tools/dumps/
  PlayerSpellsFrame_Spellbook_2026-11-25.txt, complete). Book art:
  .BookBGLeft spellbook-Page-Left-C60, .BookBGRight spellbook-Page-
  Right-C60 (parchment pages) -> dark navy pages (decide: keep a hint of
  book? default navy panel + thin blue center line). Category tabs on
  .SpellBookFrame.tabSystem: square icon tabs, .SquareBackground
  spellbook-Tab-Frame-C60, active spellbook-Tab-Frame-Glow-C60 +
  -glow-gradient-C60 -> navy square, gold edge when active (our tab
  styler draws a box on .Text which is 1x10 here: special-case square
  tabs, style around .Icon instead). Section header: Frame 448x60 with
  .Text, .Border spellbook-divider, .Backplate spellbook-list-backplate
  -> gold header text + blue line. Spell entries (216x60, named by
  spell): .Backplate spellbook-item-backplate -> faint navy row; .Button
  .Border spellbook-item-iconframe (active) / talents-node-circle-gray
  (passive, round) -> blue square frame / blue ring; hover
  spellbook-item-iconframe-hover / -passive-hover -> blue glow; keep
  .Icon, Cooldown, glows. .SettingsDropdown common-dropdown-a-button,
  .SearchBox (bronze common-search-border-*: fade, same as Talents).
  .PagingControls Prev/Next tex 130864-130869 (old round page arrows)
  -> our chevrons. .MaximizeMinimizeButton (RedButton-Condense) shown
  here -> navy box (queued).
  BAGS = AetherPackFrame (our own window, already Aether-styled; dump
  06:36, tools/dumps/AetherPackFrame_2026-11-25.txt, 1472 lines, near
  the 1500 cap: item buttons are ~25 lines each). Nothing for AetherSkins
  to do. Note for AetherPack: item buttons still carry Blizzard's
  NormalTexture tex 130841 (64x64 quickslot frame) and HighlightTexture
  130718 (shown in dump as visible) -> check in game whether the gray
  square frame shows behind our slot look; if so, SetNormalTexture("")
  / alpha 0. Dump cap: raise to 2500 or fold repeated item buttons
  ("N more like this") next time.
  VENDOR = MerchantFrame (dump 06:36, tools/dumps/MerchantFrame_2026-
  11-25.txt, complete; window chrome, inset, tabs, close all styled).
  Item tiles MerchantItem1..12: <name>SlotTexture tex 130766 (old
  square slot) + <name>NameFrame tex 136423 (brown name plaque) ->
  fade both, draw a navy rounded tile per item with a blue icon frame.
  ItemButton NormalTexture 130841 (64x64 quickslot) -> fade; keep
  IconBorder (quality color). Prices: Coin-Gold/Silver/Copper icons
  (keep; they're money). MerchantFrameBottomLeftBorder atlas UI-
  Merchant-BotFrame (bronze footer) -> fade, blue divider line.
  SellAllJunk / RepairAll / RepairItem / GuildBankRepair buttons: slot
  tex 130766 behind -> navy square icon buttons. Buy-back tile same as
  items (+ common-icon-undo). MerchantMoneyBg tex 525911 (L/M/R) ->
  fade (MoneyInset already styled). Page arrows MerchantPrev/
  NextPageButton (hidden here) -> chevrons. .FilterDropdown hidden.
  Tab 2 = Buyback page (BuybackBG hidden) -> dump with that tab.
  WORLD MAP = WorldMapFrame (dump 06:37, tools/dumps/WorldMapFrame_
  2026-11-25.txt, complete). NOT SKINNED in game: no [styled] marks,
  close button red. Its chrome lives under .BorderFrame (.NineSlice,
  .PortraitContainer, .TitleContainer, WorldMapFrameCloseButton,
  .MaximizeMinimizeFrame RedButton-Expand) -> skinner must look in
  f.BorderFrame when f.NineSlice is missing (map frame). Keep the map
  art (.ScrollContainer.Child tiles), fog, pins. .OverscrollBG gamepad-
  mapquestlog-bgtile-2k + vignettes -> navy. .navBar (tex 516764 bar,
  buttons tex 516763 left/arrow/selected, HomeButton, MenuArrowButton
  tex 796424/423808) -> navy breadcrumb pills, blue chevrons, gold text
  on the current zone. .WorldMapTrackingOptionsButton (common-dropdown-
  a-button) and .WorldMapTrackingPinButton (tex 136467 bg, 136430
  border, Waypoint-MapPin-Untracked) -> small navy round buttons.
  .SidePanelToggle (QuestCollapse-Hide-Up + MapCornerShadow-Right) ->
  navy chevron tab. Player coords label (.PlayerCoords) bottom - leave.
  QUEST LOG SIDE PANEL QuestMapFrame.QuestsFrame / QuestScrollFrame:
  .Background QuestLog-main-background (parchment), .BorderFrame .Border
  QuestLog-frame + .TopDetail QuestLog-frame-filigree + .Shadow ->
  navy panel; .Edge questlog_line_scrollbar -> blue line; zone headers
  289x22 common-button-list-collapseExpand + plus/minus (same as rep:
  navy strip, gold text); quest rows: .HighlightTexture QuestLog-quest-
  glow-yellow -> blue glow; .Checkbox QuestLog-icon-ticksquare +
  .CheckMark QuestLog-icon-checkmark-yellow -> our box + gold check;
  objectives .Dash/.Text; POI buttons UI-QuestPoi-QuestNumber + icons
  (Quest-In-Progress-Icon-yellow, UI-QuestIcon-TurnIn-Normal) -> same
  as the tracker icon overlay (AetherLedger_TrackerLook); SearchBox and
  QuestLogCount bronze common-search-border-* -> fade/our input; gear
  .SettingsDropdown QuestLog-icon-setting -> white glyph. Hidden: side
  tabs QuestsTab/EventsTab/MapLegendTab, DetailsFrame (quest detail
  page) -> dump with a quest clicked. AetherPathfinderButton (ours) ok.
  OPEN Q to user: show ALL finished quests (any zone) at the bottom, not
  only ones from here? (5.9 note: "there may be more").
- LAST BUILD (Nov 25, 07:35; user 07:27 "go ahead with the build"):
  AetherSkins 1.3.0 (second pass, new AetherSkins_Pass2.lua: atlas/file-ID
  rules + SetAtlas post-hooks; side tabs, headers, capsule bars, talents,
  spellbook, roles, merchant tiles, world map via BorderFrame, max/min
  buttons; new media from tools/gen_skins_art2.py; test skins_pass2_test),
  AetherLedger 1.8.3, AetherPack 1.6.2 (quickslot frame faded, blue slot
  frame). UNVERIFIED IN GAME: talent 'can take' detection (Glow /
  SelectableGlow / SelectableIcon shown), GetNodeInfo ranks, Line
  texture orientation of the 3D shafts, spell item RequiredLevel text.
  NEXT: Hub cleanup (inventory -> mockups), quest dialog dump.
  Checklist doc for this build: https://claude.ai/artifact/XvgN21CTknwxXLLPLwARsa
  (sections 1-4, Result enum Pass/Partial/Fail/Not tested/Can't test now).
  QUEST DIALOG dump (07:40, tools/dumps/QuestFrame_Reward_2026-11-25.txt,
  reward page): QuestFrameRewardPanelBg atlas QuestBG-Parchment (Detail/
  Progress/Greeting panels likely the same); reward items QuestInfo
  RewardsFrameQuestInfoItemN: NameFrame tex 136796 (brown plaque),
  IconBorder 651080; XP .ValueText; Complete button styled. Mockup
  mock/pass2_quest.py: A keep parchment (tiles navy) / B navy page (gold
  title+headers, light body text, navy tiles) - my pick B; B needs the
  quest font objects (QuestFont, QuestTitleFont, QuestFontNormalSmall...)
  recolored light, which also changes the map quest log detail page
  (fade its parchment too). CHOSEN 08:36: option 3, new Aether page
  (mock/pass2_parch.py build(3)) for quest, gossip and map quest details.
  SLIDER (08:45): every skinned window's scroll bar -> BEVELED gold thumb
  (sharp center ridge, dark left facet, lit right facet, thin dark rim;
  mock/slider3d.py thumb 'bev'), thickness as in the quest mock (~6 UI
  units), dark navy track, arrows = our 3D gold chevrons (chev3d_up/down
  + win_chev_dark backing).
  SIDE TABS (08:48): flat gold glyphs on navy for non-character tabs
  (banner=Reputation, hammer+pick=Skills, shield+blades=PvP, coin stack=
  Currency, bar chart=Statistics; Character tab keeps the portrait); open
  tab = B: thick gold frame (3px) + gold notch + soft gold glow (mock/
  sidetabs_flat.py).
  CRESTS + OTHER TABS (08:55): "Both". Flat gold-on-navy crests (map,
  book, talent tree, magnifier, friends, progress track; character windows
  keep the portrait) and flat side tabs on Friends, Group Finder and
  Progress Track in the same B style (mock/crests_flat.py).
  VENDOR (09:05): A, cards. Keep Blizzard's 2x5 grid; navy cards with
  edge, quality frame (>=2) else blue, light names/prices, gold page
  chevrons, empty tiles hidden, Merchant/Buyback as aligned pills under
  the window. Flat buttons: anvil+hammer=repair all, hammer=repair item,
  shield+hammer=guild repair, coin sack=sell junk (mock/vendor.py,
  glyph_img -> gen art at 4x then reduce).
  TALENT VISIBILITY (09:12): Proposed. none = icon ramp (24,48,92)->
  (120,160,220), frame (110,150,210), navy backing plate (30,58,104,a150)
  4px around; lock = gray*0.85+25, frame (125,129,140), arrows
  (150,154,164); hide DisabledOverlay (mock/talent_full.py VIS=1).
  NEW PLAYER FRIENDLY (09:18): B, sprout glyph (role_newcomer) on the
  4th Group Finder button; clamp it to the 64 size (mock/npf.py).
  BAG FRAMES (09:22): B, frame colour = item quality when >=2 (uncommon
  and up), Aether blue otherwise (mock/bagq.py).
  RESIZE (09:24): corner grip. Small gold grip bottom-right on every
  skinned window except quest windows; drag = SetScale (clamp 0.7-1.5),
  saved per window name in AetherSkinsDB.scale; right-click = reset.
  Character right-panel section pills -> navy (user, checklist).
  CHARACTER SLOTS DUMP (08:59, tools/dumps/CharacterFrame_Slots_2026-11-
  25.txt): each Character<X>Slot has NormalTexture 130841 (64x64, ours
  already), .BorderFrame child texture atlas UI-Character-Info-GearSlot
  55x55 = the BRONZE frame with corner studs -> fade; .IconBorder tex
  651080 = Blizzard quality edge (green etc.) -> fade, colour our frame by
  GetInventoryItemQuality("player", slot:GetID()) >=2 else blue (same as
  bags; refresh via hooksecurefunc PaperDollItemSlotButton_Update).
  Ammo: UI-Character-Info-GearSlotSmall (fade -> our frame) and
  UI-Character-Info-GearSlot-Arrow (orange arrow -> tint gold).
  PaperDollSidebarTab1-4 (top of right panel): UI-Character-Info-StatTab
  (+ -Selected) -> W.SquareTab style (navy box, gold frame when selected).
  Model buttons: common-button-square-gray-up/-down -> NavyBox, icon gold.
  SPELLBOOK BROWN = spellbook-item-iconframe-passive (blue = iconframe);
  fade both (+ -hover, -shadow) and draw our blue frame.
  PACK AMMO HEADING (09:20, user idea; mock/pack_full.py V=3): the Ammo
  section header reads "<Name>: <count>" (name + colon in gold, count
  dim): Arrows (bow/crossbow or quiver), Bullets (gun or ammo pouch), Soul
  shards (warlock / soul bag). Right side of the header line: buy hint,
  "buy N stacks to fill" (light text; red at AMMO_LOW), N = floor(room /
  stack), room = quiver capacity - ammo in it; "quiver full"/"pouch full"
  in green when N = 0 and no room; warlock "room for N more". Header line
  stops before the hint. Bottom Ammo row STAYS (only warning when you have
  no ammo and the section is gone).
  TWO BUILDS (09:19, user): Build 1 = BUG FIXES only: lazy ScrollBox rows
  (acquired/initialized callbacks + fallback timer), rep capsule fit to
  .FillArea, light text on navy (spellbook names/ranks/headers, gossip,
  quest), talent visibility (none/lock + DisabledOverlay + can-purchase
  glow flag + solid gray shafts), spellbook iconframe(-passive) fade + our
  frame, Group Finder (NPF clamp to 64, red close, side tabs styled as
  plain navy), map (header gold, zone-bar bronze, dimness), vendor
  (tab alignment, hide empty tiles, repair icons visible), friends card
  SetVertexColor hook, bag + character slot quality frames, character
  bronze GearSlot fade + ammo slot + sidebar tabs + model buttons, rep
  pills navy, tracker hand-in spacing. Build 2 = DESIGNS: flat side-tab
  glyphs + B style, flat crests, vendor A cards + flat buttons, NPF
  sprout, gold beveled slider everywhere, quest page option 3, resize
  grip, Pack ammo heading. Hub cleanup = pass after that.
  BUILD 1 CODED (09:55, branch fixes-pass2b, NOT BUILT): Skins 1.3.1,
  Pack 1.6.3, Ledger 1.8.4. Windows: tab box tied to tab CENTER at a
  per-row text offset (tabOffset); W.H.Close exported. Pass2: P.KeepTint
  / P.KeepColor (post-hook SetVertexColor / SetTextColor+SetFontObject),
  P.LightText on every FontString (lum < .35 -> TEXT), WatchList on any
  frame with .ScrollTarget (ScrollUtil acquired + initialized callbacks,
  OnShow +0.2 s fallback) -> W.Again(root) = one Contents per frame;
  capsule fitted to .FillArea +-2 / fill height + 4; quality mirror from
  IconBorder 651080 (QualityBorder) onto IconFrame edges; SpellFrame
  around Icon when iconframe(-passive) fades; RedButton-Exit -> Close;
  GearSlot(+Small) fade; StatTab/model buttons/arrow tints; Character
  stat titles (UI-Character-Info-Title) -> HeaderStrip; talents per
  decision + canPurchaseRank + DisabledOverlay always 0 + plate; gray
  arrow SetColorTexture; Role w clamp 64; MerchantTile hides with its
  ItemButton. Pack: SlotQuality (ITEM_QUALITY_COLORS >=2, IconBorder
  alpha 0). Ledger: divider +5 above block. Tests: skins_pass2 (+20),
  skins_windows (tab rule), pack_test (quality). Suite: only baseline
  failures remain (same list as before the change).
  NOT IN BUILD 1 (need info): Group Finder side tabs + its window's red
  close (tabs aren't in LFGListingFrame dump: dump the parent window with
  the tabs showing); map "dim" (need a skins on/off screenshot pair);
  talents brown background (unknown art). Vendor repair icons -> Build 2
  flat buttons.
  GROUP FINDER DUMPS (09:35): the three side tabs are three WINDOWS:
  LFGListingFrame (I, skinned), LFGBrowseFrame (magnifier) and
  LFGWhoListFrame (people) - the last two were never in W.KNOWN, hence
  Blizzard look + red close. Added to KNOWN; new art: groupfinder-Stat-
  StoneBG (fade), groupfinder-ScrollLine (blue line), common-dropdown-a-
  button-disabled / OptionsIcon-Brown / common-icon-search (light). The
  side tabs themselves are in none of the three dumps (a separate frame):
  need /skins tree pointing at a tab. NPF button also has atlas
  newplayerchat-chaticon-newcomer (20x20, the little sprout) - Build 2.
  GF SIDE TAB DUMP (09:43): ".ListingTab" 55x55, Background common-sidetab,
  Icon tex 8197096, SelectedTexture/TabGlow common-sidetab-selected,
  HighlightTexture common-sidetab-hover: same as Character side tabs but
  parented outside the windows. Fix: LooseSideTabs() in W.AfterWalk scans
  UIParent's children (non-windows) for kids with a common-sidetab
  Background + SelectedTexture -> P.SideTab; throttled 2 s; LFG* windows
  then drop the right chevron.
  BUILD 1 SHIPPED 09:45 (main, zip sent): Skins 1.3.1, Pack 1.6.3,
  Ledger 1.8.4. Still open: map dimness (screenshot pair), talents brown
  background (Talents /skins tree).
  BUG (09:48, branch fix-ledger-landing, READY, NOT SHIPPED): "To Cork
  Gizelton (Desolace)" said fly Orgrimmar -> Thunder Bluff (Tal), then
  walk to Desolace 67,58. Landing FM picked by straight-line distance;
  Thunder Bluff about as close as Shadowprey (Thalon) but behind
  mountains. Fix: Landing() in AetherLedger_Travel.lua prefers a known
  FM on the destination's map unless another is < 50% as far.
  tools/ledger_landing_test.py (4). User has Shadowprey. Goes into BUILD
  2 (merge with the design branch; Ledger 1.8.5).
  GOSSIP TEXT STILL DARK (09:51 screenshot, Doras): if Build 1 was
  installed, LightText missed gossip text; asked user to confirm and
  /skins tree pointing at the gossip text.
  Resolved: user hadn't installed Build 1; with it the text is light.
  GOSSIP OPTIONS (09:56): option text (e.g. "I need a ride.") in Aether
  blue (B, mock/gossip_opt.py) -> BUILD 2. Gossip option buttons: Button
  in GreetingPanel.ScrollBox rows with .Icon + a FontString (tex 136810
  highlight); P.KeepColor(fs, BLUE) on those. Dark background confirmed
  intended until Build 2's Aether page (option 3).
  BUILD 1 TEST (10:18, user): 1 pass (gold slider = Build 2). 2 Friends
  too dark, hover = selection (mock/friends_sel.py, asking). 3 pass, but
  rare blue vs empty/plain blue alike (asking). 4 pass, locked still
  dark. 5 page arrows enabled ~ disabled; brown frames remain on
  unlearned spells (Multi-Shot) with dark names (need /skins tree on
  one). 6 pass. 7 map quest log headers still brown/white (rows made on
  log update, old ScrollFrame). 8 pass; gossip text -> Build 2 blue;
  vendor page arrows too dark/alike. 9 pass. 10 divider barely better.
  FIXED on branch fixes-build1-feedback (from main + fix-ledger-landing):
  page arrows (LIGHTID: GetDisabledTexture -> dim .3, else .86/.93/1),
  talents (P.UnspentPoints via UnitCharacterPoints/GetUnspentTalent
  Points: 0 -> not "can"; Icon SetVertexColor hook; lock icon .92,
  frame .62/.65/.7), map quest log (hook QuestLogQuests_Update /
  QuestMapFrame_UpdateAll -> Again(WorldMapFrame)). Tests +4.
  FRIENDS (10:25): A - lighter cards, hover thin blue outline, selected
  brighter + blue outline + gold notch (mock/friends_sel.py) -> Build 2.
  TRACKER LINE LATE (10:27): after /reload the line came ~6 s later
  (first Apply at 6 s; line drawn only on a module Update). Fixed on the
  branch: first Apply at 1.5 s + again at 6 s; Apply calls
  AetherLedger_TrackerLook.Repaint() (also on the no-change path).
  ITEM FRAMES (10:30): A - empty slots dim slate (52,64,84), plain items
  (white/gray quality) silver (200,205,215), uncommon+ quality color.
  Character slots (QualityUpdate: no IconBorder/common -> silver if an
  item, slate if empty: check GetItem/Icon texture) and Pack
  (SlotQuality) -> Build 2 (mock/slot_colors.py).
  SPELLBOOK BROWN (10:25): Multi-Shot fine after a reload, so it was
  timing (an entry filled in after our walk). Branch: hook SetCurrentPage
  on paged frames -> Again(root); every window also looks again 0.3 s
  and 1 s after it opens (LookAgainLater). No dump needed unless it
  recurs.
  PET PAGE DUMP (10:27, tools/dumps/PlayerSpellsFrame_Pet_2026-11-25.txt):
  Growl uses the same spellbook-item-iconframe; its entry frame differs
  (no hidden 37x10 FontString = made later) -> same timing cause, fixed
  by LookAgainLater/SetCurrentPage. Autocast spells (Growl, Bite) have
  .AutoCastOverlay with atlas spellbook-item-petautocast-corners (brown
  corners) -> now tinted gold (GOLDT).
  HOVER DUMP (10:29, tools/dumps/PlayerSpellsFrame_Hover_2026-11-25.txt):
  the brown entry is the one under the MOUSE (Arcane Shot; Growl before):
  IconHighlight shown, Arrow ...Flyout-Mouseover, and that entry lacks
  the hidden 37x10 FontString (Blizzard redraws it). Fix: P.SpellRestyle
  (Visit item, Button, TextContainer, AutoCastOverlay + SpellUpdate) on
  each entry's UpdateVisuals/OnEnter/OnLeave and Button OnEnter/OnLeave,
  plus hooks on SpellBookItemMixin (UpdateVisuals/OnEnter/OnLeave/Init)
  for entries made later. Test +1.
  TRACKER HAND-IN MARK (10:35): no text label (gap too small, would
  overlap). Chosen B: quests below the gold line get a BLUE ring and a
  blue check mark in place of the gold "?" (mock/trk_check.py); gold line
  kept. Code: AetherLedger_TrackerLook ghost icon (trk_ring + "?" font
  string, ~line 200) -> when ElsewhereZone(id): ring BLUE, mark = check
  (draw a check glyph texture, not a font "?") -> Build 2.
  BUILD 2 CODED (10:55, branch build2 = fixes-build1-feedback + designs,
  NOT BUILT): Skins 1.4.0, Pack 1.6.4, Ledger 1.8.5. New file
  AetherSkins_Pass3.lua (toc after Pass2): P.SideTabExtra (glyph by
  icon file ID / friends atlas / parent key; 2 extra gold rings + gold
  glow_sq when open), P3.Crest (portrait faded, disc_plain navy + gl_*
  gold; PlayerSpellsFrame switches book/talents), P.ExtraRule (vendor
  SpellIcon-256x256-* -> btn_*; minimal-scrollbar thumb -> sb_thumb_*,
  track navy, arrows chev3d_up/down 14px; QuestBG-Parchment ->
  page_aether + blue edge; friends-card-selected -> notch + edge, hover
  edge in HIGHLIGHT), P3.Headings (gold QuestInfo headers), gossip
  choices blue (GossipFrame buttons with .Icon), P3.Grip (not Quest/
  Gossip/QuestLogPopupDetail; SetScale 0.7-1.5, AetherSkinsDB.scale[name],
  right-click reset). Pass2: P.ExtraRule hook, P.SideTabExtra hook, P.H
  helpers, silver/slate item frames, NPF -> role_newcomer, chat sprout
  icon faded, 136796 reward plaques navy. Art: tools/gen_skins_art3.py
  (run from mock/). Pack: AmmoHeading (Arrows/Bullets/Soul shards, buy N
  stacks / quiver full / room for N), silver/slate frames; test
  pack_ammo_heading_test.py. Ledger: trk_check.tga, blue ring + check on
  hand-ins (tracker_look_test +2). NOT DONE: map quest DETAILS page
  (no dump yet), map dimness, talents brown background.
  BUILD 2 SHIPPED 10:42 (main). BUG 10:55 (user): Lua error opening a
  map quest log header: MinimalScrollBar thumb OnSizeChanged calls
  C_Texture.GetAtlasInfo(self.Begin:GetAtlas()) - our Build 2 thumb rule
  had SetTexture'd the thumb parts (dump: Thumb .Begin tex=-567). FIX
  (branch fix-scrollbar-atlas, Skins 1.4.1): Ours() now lays our art on
  a texture of OUR OWN over Blizzard's (same layer +1, mirrors shown and
  desaturated) and fades Blizzard's; Blizzard's atlas is never replaced.
  Used for thumb, arrows, vendor icons, quest page. Also Ledger 1.8.6:
  hand-in check GOLD, ring gold (user 10:55, mock/trk_check.py A).
  DECIDED 10:55: map quest log POI icons tracker-style (navy disc, gold
  ring+dots; turn-in = gold ?/check) + track boxes navy w/ blue edge
  (mock/maplog_icons.py); talent class art KEPT; map log background:
  user wants a blue instead of near-black (mock/maplog_bg.py, asking).
  Ledger idea (user): click a finished quest's tracker icon -> directions
  to its turn-in NPC; Hub toggle on the Ledger tab -> with Hub cleanup.
  Map quest DETAILS page still needs a dump (click a quest in the log).
  FIX BUILD SHIPPED 11:05 (main): Skins 1.4.1, Ledger 1.8.6.
  MAP LOG BACKGROUND (11:10): B - Aether blue at 45% (35,75,115) behind
  the map quest log (QuestLog-main-background area; mock/maplog_bg2.py),
  navy header strips stay. With the POI icons + track boxes -> next build.
- SHIPPED 07:35 (branch skins-second-pass): AetherLedger 1.8.3 -
  hand-in list at the bottom of the tracker now takes finished quests
  from ANY zone whose turn-in isn't here (user 06:41, screenshot in
  Desolace: Supply and Demand, a Stranglethorn quest, missing). Answers
  the open "all finished quests?" question: yes. Test: tracker_handin.
- LAST BUILD (Nov 25, 06:30; user 06:24 "go"): AetherLedger 1.8.2 (hand-in
  zone from C_QuestLog.GetNextWaypoint first), AetherSkins 1.2.2 (full
  /skins tree dumps: 1500 lines, hidden parts folded, our pieces skipped;
  SocialUIFrame in W.KNOWN). NEXT: user dumps Reputation, Friends list,
  Talents, Progress Track, Group Finder, Spellbook, Bags, a vendor, quest
  dialog, world map; then the skins second pass.
- LAST BUILD (Nov 25, 05:50; user 05:33 "go ahead with all the fixes and
  recommendations"): AetherLedger 1.8.1, AetherSkins 1.2.1, AetherHub 1.14.8.
  * Errors fixed: Ledger GiverText order (Hub Ledger tab / moving givers),
    Skins secret-text guard (Debug Skins, Copy Full Report). Skins tab boxes
    centered on their text.
  * Check Zones Now: "Here, <ZoneShort>." (or "no quests left for your
    level") right above the zone list; "<zone> is still your best zone.
    Others for your level:" when here ranks first.
  * TRACKER HAND-INS (user pick "bottom of tracker", 05:33; divider asked
    05:35): finished quests whose home is here/focus and turn-in is not
    here stay tracked, added FIRST so they sit at the BOTTOM (newest-on-
    top tracker), sorted by title, trimmed first if over the watch cap;
    AetherLedger_Tracker.ElsewhereZone(id) -> zone name; TrackerLook:
    Ready line -> "Ready for turn-in: <zone>" (prefix match, no double
    append, stays Aether blue) and a gold trk_line divider on top of the
    topmost such block (one per module, hidden when none).
  * RED QUEST NOTE (user's option 2): QUEST_ACCEPTED remembers the id; the
    next Apply prints once "<title> is red for you right now (level N), so
    it's off the tracker until you level up. Shift-click it in your quest
    log to keep it on." tracker_handin_test (new).
  * /skins tree (point at a window): AetherSkinsDB.lastTree = {name, lines}
    (kind, name or .parentKey, size, hidden, atlas/tex, [styled kind];
    depth 5, 400 lines, no text); Hub Debug "Show Window Dump" + in Copy
    Full Report. Ask the user for dumps of Character, Reputation, Friends,
    Talents, Progress Track before the second pass.
  * NOT DONE, user asked (05:35): quest list 10-20 px lower (too close to
    the zone/clock pill). Nothing of ours moves the tracker (Edit Mode
    does); moving ObjectiveTrackerFrame from addon code taints Edit Mode,
    so suggested a one-time Edit Mode drag (Hub Layout: Open Edit Mode).
    RESOLVED (06:03): user moved it in Edit Mode; layout and action-bar
    alignment were unaffected. Pills stay where they are.
- DESIGN, NOT QUEUED (user, Nov 25 ~04:20, checklist 2.6): "our Addons
  option list is getting long and out of control. we need to review the
  menus, combine like options, normalize button naming conventions,
  etc." -> a Hub review: inventory every tab's controls, propose a
  regrouped layout (mockups) before any change. Also open: rounded
  corners on buttons/tabs/search boxes (suite-wide recommended, 4 px;
  checkboxes 2 px) from 1.13.
- DECISIONS (user, Nov 25 04:34) for the SKINS SECOND PASS below, now
  QUEUED as a whole: (6) right chevron: HIDE it on windows with side tabs;
  (7) crest: the player's FACE (SetPortraitTexture(tex, "player"), cheap)
  on windows whose crest shows a portrait (Forever puts the class icon on
  the Character tab); (8) rounded corners suite-wide, style pending the
  mockups RoundedButtons_Hub(_zoom).png / _Talents.png (made by
  /tmp/rb/round.py on the user's screenshots: square / B subtle 3 /
  C soft 5 / D capsule): CHOSEN C, soft 5-unit radius (user, 05:31); checkboxes ~3; (9) Hub review: inventory first,
  then mockups.
- SKINS SECOND PASS, INVENTORY (from the user's checklist + screenshots,
  Nov 25 ~04:00-04:10; not queued yet, waiting on 2 decisions: right
  chevron (c) move past Forever's side tabs?; crest = player portrait on
  every tab, or keep Forever's class icon on Character?):
  WORKED: outer frame everywhere, title strip, close box, crest disc,
  Add New Friend + Apply Changes buttons, Reputation checkboxes, gold
  text, Talents' bottom-style tabs (Primary/Secondary) + its search box.
  TO DO: Forever SIDE TABS (Character/Reputation/... column, Friends'
  column, Progress Track) navy + blue edge, gold selected; RIGHT CHEVRON
  hidden under side tabs; title gold sticks (Character title = player
  name, Blizzard recolors it white); stat category headers + rep
  faction headers + "Friends List 1/2" header -> tracker-style header;
  rep bars -> capsule bars, Neutral Aether gold, Friendly+ #22e650;
  selected row -> blue band; scroll bars (Forever's not MinimalScrollBar:
  ours looked murky green on rep) -> clearly Aether blue; panel
  backgrounds + divider (CharacterFrame InsetRight etc. brown) -> dark;
  equipment slot frames brown -> faded (keep quality borders); small icon
  buttons (friend invite, ☰ menu, status/clock dropdown, Talents' ▼)
  -> navy, glyphs white; Filter button; Forever's search box (Friends: no
  blue edge, different build than SearchBoxTemplate); yellow glyphs
  (model zoom/rotate, ◀ collapse) -> white. Ask for /skins debug from
  each window (Debug page copy) to get Forever's part names.
- LAST BUILD (Nov 25, 04:20; go-ahead 03:49): AetherLedger 1.8.0 + AetherHub
  1.14.7 (rest unchanged from 03:45).
  * Ledger tracker icon (1.7.2 fix, merged): overlay parented to the BLOCK,
    anchored to the POI button (Blizzard's AddAnim scaled the button and
    our child disc filled the screen on Forever); Blizzard's own button
    regions + children SetAlpha(0) so nothing of theirs balloons either.
  * Quest ZOOM (user pick b): AetherLedger_TrackerZoom. QUEST_ACCEPTED marks
    the quest (a2 or a1 = questID, 6 s window); next StyleIcon for that
    block.id plays our AnimationGroup: Scale 25->1 (OUT) + Alpha 0->1 over
    35%, 0.6 s, once. QUEST_TURNED_IN: a ghost copy on UIParent (HIGH) at
    the icon's spot plays Scale 1->25 (IN) + Alpha 1->0. Off with the
    tracker look (Wants()). tracker_look_test (+10 checks).
  * MOVING QUEST GIVERS: new AetherLedger_Routes.lua (18 KB, 61 quests, 28
    walkers) from QuestieDB Forever npc field 8 (waypoints), by
    tools/extract_routes.py <folder with foreverQuestDB.lua, foreverNpcDB.lua,
    areaIdToUiMapId.lua> (clone github.com/Questie/QuestieDB, data/Forever
    + support/Forever/Zones). Path thinned to 1-unit steps, cap 80, span
    >= 3. Companions share a walker's route only if within 1.5 units of its
    start AND the route spans >= 25 (caravans; town patrols 3-12 swept in
    shopkeepers): only Rigger Gizelton (5943). Ledger: "(on the move)" after
    the giver in quest lines and the new class/profession notice; dest.qid
    on GoTo/GoToQuest; Travel: dest.route (world points), last walk aims at
    the nearest route point, arrival = within 40 yd of the route ->
    Arrived("route") flash "You're on the road!"; title "(Desolace, on the
    move)". Targeting/talking to the NPC still = "You're there!".
    ledger_routes_test (new), travel_window_test (+1).
  * HUB DEBUG PAGE: GENERAL tab "Debug" (/hub debug, /hub report); WIN_H
    500 -> 525 (saved smaller heights are raised). Buttons: Debug Bars /
    Chat / ItemID / Marks / Pathfinder / Skins, Show Ledger Status, Check
    Memory (collectgarbage + GetAddOnMemoryUsage per loaded Aether addon),
    Preview Meter; output in a multi-line EditBox (copy: Ctrl+A/C), lines
    caught by a hooksecurefunc on DEFAULT_CHAT_FRAME.AddMessage while a
    command runs, color codes stripped; Copy Full Report = versions +
    memory + every report, selected. Skins tab's Run Debug -> link to Debug.
    No Frames portrait test (its command changes the user's 2D/3D setting).
    /ledger tracker already explains each quest (the "why" command exists).
    hub_debug_test (new, 34 checks), skins_hub_test updated.
  NOT yet in game: all of the above. Checklist doc (user ticks boxes):
  https://claude.ai/artifact/BEV8UsMzQVq3k6KJn13Be1
- OPEN QUESTION (user, 03:16 video): a just-accepted RED quest ([45]
  Horde Trauma) flashes in the tracker, then AetherLedger removes it
  (red rule). Offered: 1 keep, 2 same + chat note why (recommended),
  3 keep a just-accepted quest until a zone change, 4 show red dimmed.
- LAST BUILD (Nov 24, 20:20; go-ahead 20:10): Hub 1.14.5, Coords 1.3.15,
  Pathfinder 1.9.6 (Skins 1.1.1 and the rest unchanged from 16:15).
  * AetherSkins tab in AetherHub (user, 19:54): "Minimap in the Aether
    look" switch (sends /skins minimap on|off, NeedReload), "Run Debug"
    (/skins debug), note that more windows get switches here. /hub skins.
    Sidebar now 15 tabs: fits the 500-tall default with ~6 px spare; the
    NEXT tab needs more room (taller window or tighter tabs). Test:
    skins_hub_test (new; runs without the user's SavedVariables).
  * Memory fixes below. NOT yet confirmed in game: rerun the memory line
    after a few minutes of play (should stay low for Coords/Pathfinder).
  * Still open: AetherChat copy button (user hasn't said yes/no).
- SHIPPED 20:20 (branch fix-memory, merged): AetherCoords 1.3.15.
  User's memory readout (20:02, after ~play): Coords 8858 KB, Pathfinder
  7284 KB, Ledger 3152, Bars ~2670 (inferred from total 25736), ItemID
  2064, rest 139-405. Coords has ~44 KB of code, so the number is mostly
  uncollected garbage: the minimap pin loop ran EVERY FRAME and made new
  Vector2D tables per waypoint. Fix: waypoint world positions cached
  (weak-keyed wpWorld), loop throttled to 30/s. Asked the user to rerun
  the readout after collectgarbage() to split real use from garbage.
  After collectgarbage() (20:08): total 9693 KB; Coords 78 (garbage
  confirmed), Pathfinder ~1600 (was 7284: same per-frame minimap loop),
  Bars 1517, ItemID 2064, Ledger 3152, Hub 405, Frames 273, Chat 147,
  Marks 138, Pack 158, Meter 82, Skins 80. Same branch: AetherPathfinder
  1.9.6, minimap pin layout throttled to 30/s (RebuildNearby stays 1/s).
- LAST BUILD (Nov 24, 16:15; go-ahead 16:12): AetherSkins 1.1.1 only
  (others unchanged from 15:44). What's in it:
  * /skins debug fix (user, 15:52): scans skip forbidden frames
    (Regions()/Children(), pcall + IsForbidden).
  * PLAIN NAVY RING (user, 16:11: "the whole ring navy blue, without the
    light source"): ring_day and ring_night are now baked identical to
    ring_plain (tools/gen_skins_art.py), so there's no gold/white glow and
    the day/night swap changes only the sun/moon icon. Ring light C (16:10)
    was picked, then dropped for this before shipping. The Lua's light
    code is untouched (harmless; could be simplified later).
  NOT yet confirmed in game: plain ring, /skins debug runs clean.
- CONFIRMED in game (15:50-15:53): 1.1.0 minimap layout (magnifier menu
  + hover work, Forever coords gone, pills placed, quest list clears by a
  few px), 3D chevrons on AetherHub's window.

- LAST BUILD (Nov 24, 15:44; go-ahead 15:36): Ledger 1.7.1, Skins 1.1.0,
  Coords 1.3.14, Hub 1.14.4, Bars 1.14.3, Frames 1.14.7, ItemID 1.1.4,
  Meter 1.13.9, Pack 1.6.1 (Pathfinder 1.9.5, Marks 1.6.13, Chat 1.0.8
  unchanged). What's in it:
  * Turn-in text Aether Blue (READY = BLUE).
  * 3D bevel gold chevrons everywhere: tools/gen_chev3d.py bakes
    chev3d_up/right/down/left.tga into each addon's Media (from
    win_chev_gold) and AetherFrames' chev58/chev80_<dir>_gold3d.tga (from
    each direction's own flat art, light in screen space). Gold is never
    rotated or tinted; dark backings still rotate. Mirrored (target)
    frames swap left/right art instead of flipping. Test chev3d_test.
  * AetherSkins 1.1.0 = the minimap decisions below (layout 3, ring
    light B, Aether Blue magnifier, calendar + addon compartment hidden,
    Forever's PlayerCoords hidden by name + by content). Zone pill:
    AetherSkinsZonePill, 5 under AetherCoords_MiniUnderMap() (else at its
    spot), Blizzard's zone button + clock re-anchored into it and kept
    there (SetPoint hooks); mail IndicatorFrame left of the pill;
    MinimapCluster.Tracking moved onto the ring at (-0.718R, 0.735R),
    strata MEDIUM, art hidden, our disc + ico_track (Aether Blue) with
    mouse off. Coords gap now 0.223R + 2 (chevron backing reaches 0.223R
    below the edge). Tests: skins_minimap_test (layout 3), coords_pill_
    test; render tools/skins_render.py. The parallel chat's 1.0.3 code was
    rebuilt from its transcript here (its "stop 3 short" pill code dropped:
    moot with layout 3).
  NOT yet confirmed in game: all of it. Check: chevrons on every window,
  XP bar, frames; ring light; magnifier menu opens; zone pill + clock +
  mail icon spot; quest list clears; Forever's coords gone. If off:
  /skins debug + screenshot.

- Last delivered build (Nov 24, 14:05): AetherSkins 1.0.2 (NEW: minimap),
  AetherCoords 1.3.13, AetherHub 1.14.3, AetherLedger 1.7.0 (tooltip spot
  B, sky-blue turn-in text). Others: Pathfinder 1.9.5, Frames 1.14.6,
  Chat 1.0.8, Bars 1.14.2, Meter 1.13.8, Marks 1.6.13, Pack 1.6.0,
  ItemID 1.1.3. Twelve addons now (README says twelve).
  NOT yet confirmed in game: Ledger 1.7.0, AetherSkins 1.0.2 (Forever's
  own sun hidden? pill clear of tracking/calendar? 3D chevrons),
  Coords 1.3.13 (pill under the chevron), Hub 1.14.3 (navy button).
  Seen in game before the fixes (13:58): ring, glow, our sun, zone pill
  and coordinates pill all render; 1.0.0 left Forever's sun showing.
  If anything is off: /skins debug output + a screenshot.
  CONFIRMED in game earlier (Nov 24, 10:12): Chat, Frames (gold
  chevrons), Coords (round gold glow), Pathfinder, Ledger tracker order
  and look, tapped mobs gray, Pack 1.6.0.
- PALETTE (user, Nov 24 14:31, "go with blue"): the suite's light blue is
  AETHER BLUE #4DA6FF (0.3, 0.65, 1). Official names: Aether Gold
  #FFB000 (the only yellow), Aether Blue #4DA6FF (edges, rims, glow, blue
  text), Aether Navy #13284A (title strips, buttons, pills, minimap ring).
  Aether Sky #73BFFF is retired.
- SHIPPED 15:44 (was queued (user, Nov 24 14:31): "Ready for turn-in" text
  in the quest tracker from Aether Sky to AETHER BLUE (AetherLedger_
  TrackerLook.lua READY = {0.3, 0.65, 1}; update tracker_look_test and the
  README line). Bump Ledger. Confirm the go-ahead before building.
- SHIPPED 15:44 (was queued (user, Nov 24 14:06): upgrade ALL chevrons
  in the suite to the 3D bevel ridge (A), as on AetherSkins' minimap:
  every Aether window's 12/3/6/9 chevrons (win_chev_gold in each addon's
  Media), the XP bar chevrons, the docked meter's top chevron, frame
  crests, and any other gold chevron. Use per-direction baked art lit
  from the top-right (mock/skin_chevron3d.py chevron3d('bevel', rot),
  rotate the image, no SetRotation on the gold; dark outline may still
  rotate), as in AetherSkins/Media/chev3d_*.tga. Grep all addons for
  win_chev_gold / chev58_* / chev80_* to find every use; bake matching
  sizes. Confirm the go-ahead before building (standing rule).
- SHIPPED 15:44 in Skins 1.1.0: MINIMAP DECISIONS (user, Nov 24 ~14:15-14:24, in the separate chat
  "Aether minimap coordinates bug"), part of the NEXT BUILD, waiting for go:
  * AetherSkins 1.0.3: hide Forever's OWN minimap coordinates text (the
    game option "Player Minimap Coordinates"), found by content (a pair of
    numbers) under Minimap/MinimapCluster/MinimapBackdrop, retries 2 s/6 s
    and every 15 s; /skins debug lists it. Test skins_coords_test.
  * CONFIRMED by /fstack (user, 14:59): Forever's text is
    MinimapCluster.MinimapContainer.PlayerCoords (frame) with
    .PlayerCoords.CoordText (FontString), from Blizzard_Minimap/Mainline/
    Minimap.xml:101, strata LOW level 3. Hide that FRAME by name (hook
    its Show / SetShown so it stays hidden), keep the by-content search
    only as a fallback. The 1.0.3 search (MinimapCluster, depth 4) would
    have reached it too.
  * Ring light = B: lighter soft gold-cream (ring_ref gain 0.85, peak 0.3,
    halo_amt 0.2; mock/skin_ringlight.py), rebake ring_day.
  * Layout 3: coordinates pill ~2 px under the bottom chevron; zone+clock
    pill right below it; Blizzard's tracking button moved onto the ring
    across from the sun (art hidden, navy disc + FLAT magnifier icon,
    Blizzard's click kept); calendar button hidden (our sun opens it).
    (mock/skin_mmlayout.py, mock/skin_magnifier.py)
  * Zone pill stops 3 units short of the bar's buttons (moot with layout 3).
  * Magnifier icon (user, 14:57): flat, in AETHER BLUE #4DA6FF (0.3, 0.65, 1), the blue
    picked over Aether Sky in the 14:31 comparison (not A/B/C).
  * Quest list (screenshot 14:56): header starts ~30 px below the current
    coordinates pill; layout 3 stacks both pills in about the same space,
    so it clears (re-check after build).
  * The "1" badge under the calendar = Blizzard's ADDON COMPARTMENT
    (tooltip "AddOns"; menu lists AetherHub only). CHOSEN (user, 15:01):
    option 1, HIDE it in layout 3 (AetherHub's ring button covers it).
  (That chat's branch was never pushed; rebuilt here for 1.1.0.)
- Next AetherSkins batch (looks approved, not built): world map + quest
  log, Reputation, Friends, Progress Track; then more windows. No Hub
  tab for AetherSkins yet (slash only).
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
- SHIPPED Nov 24, 14:05 (go 14:02): AetherSkins 1.0.2 + AetherCoords
  1.3.13 (user, 13:58: the zone/clock pill covered the tracking magnifier and
  the calendar). 1.0.1 sized the pill to the whole top bar; now it spans
  the zone text button to the clock (if on the same row) only, one frame
  level under them, so the bar's buttons stay clear and on top; re-placed
  1 s after login. /skins debug shows what the pill sits behind.
  Same branch: AetherCoords 1.3.13 (user, 13:59: the coordinates covered
  the bottom chevron): with AetherSkins_RingActive the readout sits
  R*0.28+4 below the minimap (chevron reaches ~0.27R), else 6;
  AetherCoords_RefreshMini, called by AetherSkins after its ring.
- 3D chevrons (accents): user picked A, BEVEL RIDGE (14:02), built on the
  minimap in 1.0.2: AetherSkins/Media/chev3d_up/right/down/left.tga baked
  by mock/skin_chevron3d.py (light from the top-right, so one texture per
  direction, not rotated in game; the dark outline still rotates).
  Windows with A accents: mockup made (14:03), waiting on feedback; not
  built for windows.
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
  meter_test, meter_test2, names_test*, radar_test, tracker_test,
  hub_general_test, itemid_test, ledger_full_test, marks_namekey_test,
  marks_plates_test, pack_class_test (all fail on shipped main too).
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

- Nov 25, 2026 (05:50): built Ledger 1.8.1 (fixes, Check Zones shows your
  zone, hand-ins at the bottom with divider, red-quest note), Skins 1.2.1
  (fixes, /skins tree), Hub 1.14.8 (Show Window Dump).
- Nov 25, 2026 (04:20): built Ledger 1.8.0 (icon fix, quest zoom b, moving
  givers) + Hub 1.14.7 (Debug page). In-game checklist made as a doc.
- Nov 25, 2026 (03:45): built AetherSkins 1.2.0 (all Blizzard windows,
  generic skinner) + Hub 1.14.6 (windows switch).
- Nov 24, 2026 (20:20): built Hub 1.14.5 (AetherSkins tab), Coords
  1.3.15 and Pathfinder 1.9.6 (minimap loops 30/s; memory 25.7 MB ->
  9.7 MB after GC showed it was garbage). Memory /run line must stay
  under 255 chars (chat box limit).
- Nov 24, 2026 (16:15): built AetherSkins 1.1.1 (debug fix + plain navy
  ring, no light source).
- Nov 24, 2026 (16:00): session closed; AetherDev.zip made. GITHUB IS
  BEHIND: this session couldn't push (no repo access granted). origin/main
  is at 18dcc02. Push main AND branch fix-debug-forbidden first thing
  (git -c push.negotiate=true push origin main fix-debug-forbidden).
- Nov 24, 2026 (15:44): built Ledger 1.7.1 (Aether Blue turn-in), 3D
  chevrons suite-wide, AetherSkins 1.1.0 (minimap layout 3), Coords 1.3.14.
  Lesson: a parallel Aether chat (14:07-14:24) made decisions the dev zip
  never got. At session start, check recent_chats for other Aether chats
  since the dev zip's last commit and read them.
- Nov 24, 2026 (14:06): session closed; AetherDev.zip made for the next.
- Nov 24, 2026 (14:05): AetherSkins 1.0.2 (zone pill, 3D chevrons),
  AetherCoords 1.3.13 (coordinates below the chevron).
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
- BUILD 3 (branch build3, NOT BUILT; user 11:36 + 11:44):
  Reputation thumb white -> Windows.Scroll no longer tints thumb, Ours()
  mirrors desaturation only when o.mirrorDesat. Selected side tab: old
  notch hidden. PvP: honor bar glow faded, LevelBG blue, bar BGs navy.
  Friends: own navy card fill; picked friend (Blizzard LockHighlight)
  brighter blue + gold notch + blue edge. Grip 14px at BOTTOMRIGHT +6,-6.
  ARROWS (user 11:44 "an enthusiastic yes", mock/arrows_vendor.py): P3
  Usable(b, o, extra) = gold when b:IsEnabled() (+extra), gray desat
  otherwise; hooks Enable/Disable/SetEnabled; events MERCHANT_*, durab.,
  money, bags refresh. Scroll arrows chev3d gold/gray. Page arrows
  (file IDs 130864-6 next, 130867-9 prev; vendor+Spellbook): Blizzard's
  faded, our chevron in a 26px navy square, blue edge (dim when off).
  VENDOR: repair buttons also need GetRepairAllCost() > 0 (repair item
  is never disabled by Blizzard). User 11:44: repair stayed gold - was
  testing the 11:05 build, which lacked this.
  MAP LOG (queued since 10:55/11:10): POI number -> trk disc/ring/dots
  (Media copied from Ledger), turn-in gold "?"; glows blue; ticksquare
  -> 12px navy box with blue edge; QuestLog-main-background -> (35,75,
  115) overlay. Tests: skins_pass2 ALL OK; suite = baseline 15.
  MAP QUEST DETAILS (user 11:58 "b it is", mock/maplog_details.py B;
  dump tools/dumps/WorldMapFrame_QuestDetails.txt): QuestDetailsBack-
  grounds -> (35,75,115) + blue edge; QuestLog-reward-top-frame/-bottom/
  -header-top/-tile-vertical -> navy; RewardsFrame.Label gold. P3.
  MapPages hooks OnShow of DetailsFrame/QuestScrollFrame/MapLegend/
  EventsFrame -> rewalk the map (hidden pages are skipped by the walk).
  Daily quests: UI-QuestPoiRecurring-* get the same disc.
  BACKGROUND TIERS (user 12:02 "different backgrounds?", 12:05 "A it
  is", mock/bg_tiers.py A): frame = PANEL (12,14,19), box = NAVY
  (19,40,74), page = H.PAGE (35,75,115) for every reading page. Page()
  (NPC quest/gossip parchment) now flat PAGE (page_aether no longer
  used). Friends cards: card NAVY, picked PAGE, offline frame-dark.
  STILL TO DO: per-window sweep of in-between tints (NAVYF {0.16,0.3,
  0.52} on textured Blizzard boxes, NAVYID, spellbook backplate, talent
  plate) -> needs in-game screenshots, after this build.
  PROFESSIONS / LEGACY / COLLECTIONS ICONS (user 12:11-12:23; dumps
  ProfessionsFrame_Overview/_Crafting, LegacySystemFrame_Tree/
  _Challenges, CollectionsJournal_Appearances):
  - BUG FIXED: Windows Kind() styled the Legacy Tree picture buttons
    (67/110px CheckButtons with .Ring) as checkboxes -> blue squares,
    pictures faded. Now only CheckButtons <= 34px without .Ring.
  - P3.MoreRule: overview/legacy cards navy + blue edge; recipe details
    page blue; recipe list navy; skill bars dark track + gold fill (Tint
    of the flipbook) + blue frame, flare faded; picked recipe blue 0.45,
    hover 0.2; Legacy rings gold, card glow blue; challenge cards navy
    (not earned: frame-dark), ribbons faded, sub-tab rows navy/blue.
  - Page arrows size to the button (Create amount arrows 23px).
  - Flat icons APPROVED 12:22 (mock/profs_flat.py, coll_flat.py): baked
    pr_*.tga (15) + cl_*.tga (5) by tools/gen_skins_art4.py; tabs by
    icon ID / CollectionsJournalTabN name; crest: ProfessionsFrame by
    portrait file ID (hooks SetTexture), CollectionsJournal by shown page.
  - NOT YET: Collections pages (Mounts/Pets/Toys/Appearances
    backgrounds) - have only the Appearances dump; need Mounts, Pets, Toys.
  COLLECTIONS PAGES (user 12:27, dumps CollectionsJournal_Mounts/Pets/
  Toys): P.ExtraID hook (Pass2 file-ID branch, before FADEID): model
  backdrop 651761/651762 -> page blue + edge; ShadowOverlay 423809-13
  faded (only under .ShadowOverlay - 423811 is also the map home button);
  130975 count pill -> blue. P3.CollRule: collections-background-tile
  page blue, shadows/corners faded, PetList rows navy (select blue .45,
  hover .2), item/wardrobe borders blue, uncollected slate, selected gold.
  Dump workflow (user video 12:27) is right: open tab, /skins tree, Hub
  Debug > Show Window Dump, copy.
- BUILD 3 SHIPPED 12:35 (main, merged build3): AetherSkins 1.5.0. README
  stamp 12:35. Next: user testing -> fix build; tint sweep (screenshots);
  Hub cleanup pass (+ Ledger click-to-turn-in directions).
- BUILD 4 (branch build4): title underline on its own frame (level +20)
  so side panels don't cover it (user 12:40). Legacy Challenges (user
  12:42 'broken'): BoxEdge was added to the hidden tiled card pieces too
  -> extra lines across each card; now one edge per card (not on tiled)
  and every BoxEdge follows its texture's shown state. OPEN: character
  crest A face / B helmet (mock/char_crest.py), asked 12:40.
  GOSSIP/QUEST PAGE (user 12:44): Page() overlay now fills the window's
  Inset (3px in), scroll bar included, edge follows; gossip options GOLD
  (was blue).
  VENDOR TOOLTIPS (user 12:46 video): Blizzard shows Repair All / Sell
  Junk tooltips only when there's something to do; P3 adds 'Nothing
  needs repair' / 'No junk to sell' (HookScript OnEnter, only when the
  tooltip came up empty).
  USER 12:57 batch: talent ghost arrowhead keeps Blizzard art (ours
  pointed the wrong way); LFG role off-glyph gray (was brown); mount/pet
  rows: box spans icon+name (LEFT anchored to .icon -4); Spellbook pages
  page blue (were faded to frame-dark). OPEN: map red quest text (mock
  maplog_red.py), Primary/Secondary text looks centered to me - asked;
  need dumps: Game Menu, talents (if arrows still wrong).
  CHARACTER CREST (user 12:59 'A'): P3.FaceCrest - navy disc + live
  SetPortraitTexture('player') masked round, refreshed on UNIT_PORTRAIT_
  UPDATE / PLAYER_ENTERING_WORLD / UNIT_MODEL_CHANGED / OnShow.
  MAP QUEST TITLES (user 13:02 yes, mock/maplog_red.py right): QuestTitle
  in W.Visit (WorldMapFrame rows with .Checkbox+.TagTexture): shadow
  0,0,0,.9 1,-1; SetTextColor hook: red->(1,.376,.345) (13:05 back from +5%), orange->
  (1,.588,.329), yellow->GOLD; green/gray kept.
  GAME MENU (user 13:04 dump): IsWindow true for GameMenuFrame; Border
  regions + Header art faded, Header.Text hidden, our title FontString
  (same words) at TOP -5; buttons get the panel-button style.
- BUILD 4 SHIPPED 13:33 (main, merged build4): AetherSkins 1.5.1.
- BUILD 5 (branch build5): talent arrows (user 13:37: gray arrow still
  double-headed, heads ran into talents): no more our arrow_head/shaft
  art, SetSize 20 or thickness 6 - Blizzard's own head + Line, Tint only
  (gold / blue / gray .62,.65,.72). Primary/Secondary text OK (user).
  TABS (user 13:39 Merchant/Buyback): like the Hub - picked tab text
  GOLD, others light gray (.85); Blizzard's tab text hidden (alpha 0,
  SetAlpha hook) and our own FontString copies its words (SetText hook),
  centered in the box, so it no longer jumps up when picked.
  SOLID WINDOWS (user 13:56): Skins window fills 0.95-0.97 -> 1 (PANEL,
  navy boxes, inputs, friend cards, tints). HUD (chat, meter, tracker,
  minimap) and AetherPack unchanged (user 13:57: keep the pack as is).
  OPEN: page blue +20% (42,90,138) everywhere - recommended, not yet ok'd.
  PAGE BLUE +20% (user 14:00): H.PAGE = 42,90,138. SWEEP 'no needless
  black': styled insets fill page blue (h<60: navy, e.g. money bar), edge
  .24,.43,.69; page-blue backgrounds: Profession overview + crafting,
  Legacy tree/challenges/rewards, groupfinder-background, Character
  stats (UI-Character-Info-Stat-BG); class art behind stats faded; Legacy
  reward cards navy boxes; LFG roles strip navy. Not changed: talent class
  art, model backdrops, title/bottom bars (frame tier).
- BUILD 5 SHIPPED 14:02 (main, merged build5): AetherSkins 1.5.2.
- BUILD 6 (branch build6). User 14:12: HATES the page blue; asked for all
  screens in navy (mock: tools-free recolor /home/claude/navy/recolor.py,
  page->navy, navy boxes->31,60,100; sheets navy_screens_1/2.png).
  Gray talent arrows untinted (Blizzard light gray). Group Finder tabs:
  TabKey falls back to GetDebugName, keys checked before icon IDs;
  Browse -> new gl_search (magnifier, gen_skins_art4.py), Who ->
  gl_people (crest too). OPEN: navy vs blue decision.
  NAVY (user 14:19 yes): H.PAGE = 19,40,74 (pages), H.NAVY = 31,60,100
  (boxes/strips/rows/tabs/crests). Gray arrows: our arrow_head_gray at
  Blizzard's size + solid light gray line .78,.8,.86.
- BUILD 6 SHIPPED 14:21 (main, merged build6): AetherSkins 1.5.3.
- BUILD 7 SHIPPED 14:26 (user 14:25 'like it a lot' black_screens mock):
  H.PAGE = 10,11,14 (near-black pages), H.NAVY back to 19,40,74 boxes.
  AetherSkins 1.5.4.
- BUILD 8 (branch build8): red quest names tried Blizzard red, user kept the LIGHTER red (14:30).
  14:28, mock/red_default.py), shadow kept; orange lifted, yellow->gold.
  RELEASE PLAN (user 14:29-14:32): A = skin polish (Skins: legacy empty
  rank boxes, Toy Box tip, 1.5.4 feedback; lighter red already on
  build8). B = Ledger: tracker click -> directions to turn-in NPC (on by
  default) + tracker quest names lighter red (1,.376,.345) + orange (1,
  .588,.329) + yellow->gold like the map (user 14:32 'go with ours').
  C = Hub cleanup (design-first, moves the directions toggle into Hub).
  GROUP FINDER TABS (user dumps 14:36): keys ListingTab / BrowsingTab /
  WhoListingTab; icons 8197096 / 8197095 / 8197123. Bug: 'WhoListingTab'
  matched 'Listing' first, 'Browse' never matched 'Browsing'. Fixed: Who
  keys first, anchored patterns, icon IDs added. P.LooseParent: the tabs'
  parent owns the portrait + red close -> our crest (glyph of the shown
  LFG page) + Close(). Not seen in game yet.
  LEGACY RANK BOXES (dump 14:42 LegacySystemFrame_Tree_b5): Talents-
  Square-Box-c60 on nodes whose StateBorder is Legacy-Tree-Frame-icon-
  frame* -> faded; blue-edged pill (PH.PillOn, ARTWORK) behind SpendText.
  Toy Box tip: user thought 'toys'; it's the one-time HelpTip - dropped.
- RELEASE A SHIPPED 14:44 (main, merged build8): AetherSkins 1.5.5 (Group
  Finder tabs/crest/close, Legacy rank pills). NEXT: Release B (Ledger
  directions on click + tracker colors) - user may continue Saturday.

## Release B shipped (Nov 25, 14:55)
- AetherLedger 1.8.7: click a finished quest's tracker icon -> waypoint
  + directions to the turn-in NPC (AetherLedger_GoToTurnIn, via
  C_QuestLog.GetNextWaypoint; off when AetherLedgerDB.turnInDirections
  == false; Hub toggle comes in Release C). Tracker red/orange names
  lifted to map-log colors with a dark shadow.
- AetherSkins 1.5.6: gray talent arrow shafts thinned (SetThickness 3);
  user 14:48 said gray was "out of whack" (fat shafts).
- Untested in game: turn-in click, thin gray shafts.
- Next: Release C (Hub cleanup), design-first, fresh session.
- Nov 25, 2026 (14:55): session closed; AetherDev.zip made. Start
  Release C: inventory each Hub tab, mockups one at a time, then build.

## Release C (Hub cleanup), Nov 25 session 2
- 14:56 GitHub caught up (main b085875, releaseB pushed). Push works once
  the repo is added with add_repo (push); user may install the Claude
  GitHub App so access sticks.
- 14:58 user: "Release C, whatever we agreed to before. Do not deviate
  from plan" = inventory -> mockups one at a time -> user picks -> build.
- INVENTORY (done): 16 tabs, ~58 controls + ~30 buttons; Bars settings on
  4 pages, Frames/Chat/Meter on 3; Preview Meter twice; 5 Reset Position
  buttons + Reset All; panel opacity slider lives in AetherMeterDB (gone
  if Meter is off); naming mixed (Show/Use/nouns; Debug X vs Show Ledger
  Status vs Check Memory); Restore Defaults on only 3 addons; versions
  in 3 places; Bars cooldown glow label says orange, tip says red; Ledger
  turn-in directions toggle missing.
- MOCKUP 1, tab layout (mock/hub_layout.py, out_hub_A/B/C.png, B zoom):
  A addon tabs each complete (14 tabs); B 8 tabs by what you see, addon
  bands inside, Unlock to Move + Reset Positions... in the footer (my
  pick); C groups folding in the sidebar. Asked the user to pick.
- 15:12 CHOSEN: layout B (8 tabs by what you see; Unlock to Move +
  Reset Positions... in the footer).
- MOCKUP 2, Unit Frames page (mock/hub_frames.py, out_hub_frames.png +
  _full.png): bands Frames / Portraits / Fading / Buffs. Slash-only
  AetherFrames options added to the Hub, tagged NEW: tot, portraits
  3d/2d, classglow, levelglow, hits, hitnumbers, aggro, combatalpha.
  Dropped: Reset Pet Frame Position (Line Up + footer reset cover it).
  Restore AetherFrames Defaults... needs a new /af defaults command.
  Waiting on the user's verdict.
- 15:14 RULE (user, suite-wide): EVERY option gets a Hub control; slash
  commands stay only as backup / preference. Unit Frames page approved
  with all NEW options.
- MOCKUP 3, Action Bar Area (mock/hub_bars.py, out_hub_bars(_full).png;
  hub_layout.render_b renders any B page): bands Panels (bars+chat panel
  switches, panel opacity in/out of combat), Action bars, XP bar (NEW
  width/height sliders = /cb xp width|height), Chat, Meter (Preview
  Meter here, not on Debug). Open Edit Mode moved here. Cooldown glow
  label = orange -> green (matches the code; fix tooltip + /cb help
  'red-to-green'). Page Restore Defaults... = this page's addons, asks
  first. Plan: panel opacity stops living only in AetherMeterDB so it
  works without the Meter (shared Hub setting the addons read).
- TALENT ARROWS (user 15:16-15:19, screenshot): "every reload the talent
  page looks different" = Blizzard POOLS arrows (same head+line reused for
  another link each refresh) and our styling left leftovers (gray line's
  solid color + thickness 3, gold tints on gray/ghost heads, Blizzard's
  shaft re-set without its head). Measured on the screenshot: long gold
  shafts 5 px flat, two BM shafts 1 px (Blizzard's thin art), gray 4-5 px.
  USER SPEC: all arrows the width of the long gold ones, no 3D, no double
  heads; KEEP the gray hue (0.78, 0.8, 0.86).
  READY, NOT SHIPPED (branch fix-talent-arrows, AetherSkins 1.5.7):
  P.Arrow styles every arrow from scratch for its state: our flat head
  (Media/arrow_head_flat.tga, tools/gen_arrow_flat.py: white, the gray
  head's shape) tinted gold / Aether blue / light gray; shaft = solid
  SetColorTexture in the same color, SetThickness 3.25 (~5 px); ghost =
  blue at 55%. Hooks the shaft's SetAtlas/SetTexture too. skins_pass2_test
  (pool order test, ALL OK, 111).
- VENDOR (user 15:22 video): Repair an Item + Sell All Junk show
  BLIZZARD'S tooltip, so our 'nothing to do' note (only filled empty
  tooltips) never showed; Repair All's note was gray. Buyback tab showed
  Blizzard's gold label above ours (user: 'good catch').
  READY, NOT SHIPPED (branch fix-vendor-tips, off fix-talent-arrows; same
  AetherSkins 1.5.7): note added under Blizzard's tooltip when idle
  (repair: GetRepairAllCost == 0; junk: C_MerchantFrame.GetNumJunkItems
  == 0, else button disabled), title + note both Aether gold, no double
  add; TabColor hides every Blizzard FontString on the tab on each
  pick/unpick (cause not confirmed by dump; if it recurs, /skins tree on
  the Buyback tab). Tests: skins_pass2 (+5), skins_windows (+1).
