AETHER ADDONS FOR WOW FOREVER
=============================
Last updated: November 25, 2026 (09:45)

A set of twelve addons for World of Warcraft: Forever that make everyday
play smoother: a damage meter, cleaner action bars that line themselves
up with one click, coordinates and waypoints, service NPCs on your maps,
quest and rare mob highlights, item details at a glance, a quest guide
that points you to the best zones, trainers and skinning spots for your
level, tidy bags sorted into sections, a cleaner chat that fits beside
your bars, Aether-styled player, pet and target frames, and the Aether
look for Blizzard's own windows, starting with the minimap. Each addon
works on its own, and AetherHub gathers all their settings in one
window, so you rarely need to type a command.

  Addon              Version   What it does
  -----------------  --------  -----------------------------------------
  AetherHub          1.14.8    One window with every addon's settings
  AetherMeter        1.13.9    Damage and healing meter
  AetherBars         1.14.3    Clean action bars with a cooldown glow
  AetherCoords       1.3.15    Coordinates, plus your own map waypoints
  AetherPathfinder   1.9.6     Trainers, vendors, flight masters and
                               mailboxes on the world map and minimap
  AetherMarks        1.6.13    Quest and rare mob colors, plus Rare
                               Radar to spot rares on sight
  AetherItemID       1.1.4     What an item is for, when you hover it
  AetherLedger       1.8.4     Where to quest, train and skin next,
                               with step-by-step travel directions
  AetherPack         1.6.3     Your bags sorted into sections
  AetherChat         1.0.8     Chat with the Aether look, fitted beside
                               your action bars
  AetherFrames       1.14.7    Your, your pet's, your target's, its
                               target's, and your party's frames with
                               round portrait crests
  AetherSkins        1.3.1     The Aether look for Blizzard's windows
                               and the minimap


GETTING STARTED
---------------
1. Close WoW.
2. Extract everything in AetherAddons.zip straight into your WoW Forever
   AddOns folder, usually:
       C:\Program Files (x86)\World of Warcraft\_forever_\Interface\AddOns
   The twelve Aether folders must sit directly in AddOns (not inside an
   extra folder), or WoW won't find them.
3. Start WoW. If the addons don't show up, click AddOns on the character
   select screen and turn them on.
4. In the game, type /hub. That's the one command worth remembering.

To update later: close WoW, extract the new zip over the old files, and
start WoW. Your settings are kept.


ADJUSTING EVERYTHING WITH AETHERHUB
-----------------------------------
Three ways to open it:
  - The Aether button on the edge of your minimap (a navy button with a
    fine blue rim). Left-click
    opens AetherHub, right-click gives shortcuts (check zones, directions
    to the best zone, clean up quests, show or hide the meter, reset the
    window size), and dragging slides it around the minimap. Untick
    "Minimap button" at the bottom of AetherHub (or type /hub minimap) to
    hide it.
  - A key of your choice: Esc > Options > Keybindings > AddOns >
    AetherHub > "Open or close AetherHub".
  - Type /hub (it's also under Esc > Options > AddOns > AetherHub).

The sidebar has two sections. GENERAL holds what several addons share
(Appearance, Fading and Layout), so you change those in one place.
ADDONS has a tab for each addon with only what's unique to it; where
an addon's look, fading or placement moved to a General page, its tab
has small buttons that jump there. Changes apply right away. Hover any
setting for a short explanation (it shows beside the window, so it
never covers the page), and scroll with the
mouse wheel on longer pages (a gold bar on the right shows where you
are). Click a slider's number to type an exact value. Drag the grip in
the bottom-right corner to make the window bigger: taller shows more of
each tab, and wider lets the text spread out. The size is remembered;
right-click the minimap button and pick Reset window size (or type /hub
resetsize) to go back. You can jump straight to a tab with /hub meter,
/hub bars, /hub coords, /hub map, /hub marks, /hub itemid, /hub ledger,
/hub pack, /hub chat, /hub frames, /hub skins, /hub me (Your
character), /hub look (Appearance), /hub fade (Fading) or /hub layout
(Layout). The Reload UI button turns gold when a change needs a reload,
and anything that can't be undone asks first.

  Appearance: Aether panels behind your action bars and behind your
    chat, and sizes (unit frames, the bag window, chat text).
  Fading: how solid things are. Aether panels in and out of combat
    (the meter, the panels behind your bars and chat, and the
    directions window); action bars when idle, solid in combat,
    solid under your mouse; unit frames out of combat, faces fade too.
  Layout: Unlock to Move (unlocks your unit frames, the meter and the
    XP bar together; drag them, then click Lock or Done on any of
    them), Open Edit Mode (Blizzard's, for action bars), Line Up Frames
    and Line Up and Center Frames (the same as the question AetherFrames
    asks after you move frames, any time), chat fitting
    to the left of your bars, the meter docking to the right,
    centering, Align Bars... and Undo Last Align, Fit Chat Now, and
    Reset All Positions... (unit frames, meter, bag window,
    coordinates and XP bar).
  Your character tab: your class, race, level and professions with
    their skill, read straight from the game (nothing to set up, and
    right on every character), plus every Aether addon's version.
    AetherHub's own version is next to its title, and /hub version
    lists them all in chat.
  Debug tab (/hub debug): a button for each addon's report (Debug
    Bars, Chat, ItemID, Marks, Pathfinder, Skins, Show Ledger Status),
    Check Memory (cleans up first, then each addon's KB) and Preview
    Meter. What they print shows in a box you can copy: click in it,
    Ctrl+A, Ctrl+C. Copy Full Report puts versions, memory and every
    report in the box, already selected, to paste to whoever helps.
    Show Window Dump shows the structure of the last window you
    pointed at with /skins tree (for restyling Forever's windows).
  AetherMeter tab: Window (show or hide, lock, DPS and HPS or only
    one, split into two windows), plus Preview Meter (sample numbers)
    and Reset Meter Position.
  AetherBars tab: Look (edge darkness, cooldown glow, macro names,
    default bar art), button sizes, Reset XP Bar Position and Restore
    Defaults...
  AetherCoords tab: Coordinates (minimap readout, cursor readout on the
    world map, decimal places) and Waypoints (Clear All Waypoints).
  AetherPathfinder tab: Show on the map (whose class trainers, which
    NPC types), Options (built-in locations, other faction's NPCs,
    minimap markers), and Learned NPCs (count, forgetting them).
  AetherMarks tab: Name colors (quest, rare, rare alert) and Rare
    Radar (on or off, how visible other names are).
  AetherItemID tab: turn the item window on or off, how long to hover
    before it opens, Restore Defaults... (keeps learned recipes) and
    Clear Learned Recipes...
  AetherLedger tab: What AetherLedger does for you (zone suggestions,
    rank-up reminders, profession and class quests, skinning spots,
    keeping your quest tracker on your zone, its Aether look), Check Zones
    Now, Save Quest Log to File, Clean Up Quest Log, and your three best
    zones: click one to see its quests below, or Go for directions. Under
    that: rank-ups due, class and profession quests, and where to skin.
  AetherPack tab: open it instead of Blizzard's bags, free slots on
    the backpack button, Open Bags, Reset Bag Window Position, and
    icons per row.
  AetherChat tab: hide the voice/channel/emote buttons, slim typing
    line, and restoring its defaults.
  AetherFrames tab: use them instead of Blizzard's, buff and debuff
    rows, threat glow, party frames, numbers on the pet's resource
    bar, and Reset Pet Frame Position.
  AetherSkins tab: the minimap's Aether look and Blizzard's windows'
    Aether look, each on or off (needs a reload), and Run Debug.

  Button names follow one pattern: what it does, then what it does it
  to ("Reset Meter Position", "Clear All Waypoints..."). A name ending
  in "..." asks before it acts. In a row of choices, the selected one
  is highlighted with its text in the Aether gold.

Every setting is also a slash command (listed under each addon below)
if you prefer typing.


THE AETHER TEXT STYLE
---------------------
The addons share one font, Fira Sans (the unit frames' font; included
in AetherHub\Media\Fonts under the SIL Open Font License), so the whole
set reads as one family:
  - In windows (AetherHub, AetherPack, AetherLedger, AetherPathfinder,
    and the small windows of the other addons): Fira Sans with a soft
    shadow, the gold headings a little bolder. Same sizes and colors as
    before.
  - Over the game world (AetherMeter's rows, the AetherCoords readout,
    the keybinds and counts on your action buttons): Fira Sans Bold
    with a thin black outline and a shadow, so it stays readable on
    bright scenery and when the meter fades out of combat.
  - If the font files are missing (say AetherHub was left out), each
    addon quietly keeps WoW's own font.
  - The Aether gold: every gold heading, label and accent (lines,
    chevrons, ticks, checkmarks) is one warm amber, the same as the
    AetherPack deposit slot. It's the only yellow in the suite: a
    mob's yellow level, neutral mob names, item tips and "getting
    full" warnings all use it too.


THE ADDONS
----------

AetherMeter - damage and healing meter                         /am
  Shows how much damage (DPS) and healing (HPS) everyone in your group
  is doing, using the game's own combat data.
  - Your bar always stays in the top row, marked with a gold strip; its
    number is your actual rank. Everyone else follows in rank order.
  - Scroll the list with the mouse wheel (Shift scrolls a page) when
    more players are listed than fit; the header shows "8 of 14
    (scroll)". Each new fight starts back at the top.
  - Only care about one? Choose "DPS only" or "HPS only" in AetherHub,
    the right-click menu, or with /am show dps (or hps, or both). That
    meter then gets the whole window.
  - Docked beside your bars: with AetherBars' trim on, the meter fills the
    space between your action bars and the right edge of the screen, as
    tall as the bars, the mirror image of AetherChat on the left. When
    split, the DPS and HPS windows share that space side by side. Untick
    "Meter docks to the right of your bars" on AetherHub's Layout page (or
    /am dock off) to place it yourself again; it goes back to your own
    saved spot and size. The meter remembers its docked spot, so after a
    reload it opens right there instead of hopping over.
  - Not docked: drag the window to move it and its corner to resize
    it, or lock it. Right-click it for its menu; Preview Meter there
    shows a pretend fight.
  - Tip: the meter is see-through so it stays out of the way. Click it
    (or scroll, drag or use its buttons) and it turns solid, then fades
    back 10 seconds after you stop.
  - Commands: /am show, hide, toggle, show dps|hps|both, lock, unlock,
    split, join, dock on|off, opacity in 0-100, opacity out 0-100,
    reset, test.

AetherBars - cleaner action bars                               /cb
  Flat, simple action buttons with the default bar art removed: the
  gryphons, the background, and the page up/down arrows and number
  beside Action Bar 1 (paging with your keybinds still works). Untick
  "Hide the default bar art" on the AetherBars tab and /reload to get
  them back.
  - Aether trim: your bars sit on panels with the Aether window look
    (double blue frame, soft glow, gold corner brackets with a fine
    echo, and one gold chevron). The panels and empty slots use
    AetherMeter's window colors and
    are exactly as see-through as the meter is out of combat (change
    "Out of combat" under Aether panels on the Fading page, and the bars
    follow).
    The gold corners and chevron fade to the same level, so the frame
    reads as one. Every bar has its own panel with all four gold corners;
    the bag bar and micro menu (with the keyring) share one strip. If
    panels sit too close, they're spaced apart and the corners that would
    collide are left off; Align Bars (below) spaces everything so every
    corner shows. Everything is snapped to whole screen pixels so lines
    meet cleanly. The bag strip's panel replaces Blizzard's dark
    background. Buttons get a thin blue outline. Turn it off on
    AetherHub's Appearance page (or /cb trim off).
  - The Aether XP bar (part of the trim): a pill-shaped bar with round
    ends. Navy is the XP you've earned; bright blue ahead of it is your
    rested bonus. Faint gold ticks mark every 5%, a thin gold mark
    shows exactly where you are, and gold chevrons sit at both ends and
    above and below its middle. The chevrons are sized from the bar's
    height, so they grow and shrink with it, and the bar leaves room at
    its ends so they never touch the bars beside it. Hover it for
    Blizzard's XP text and rested tooltip, as usual.
  - Bars stay fully solid. If you'd like them to dim when you're not
    using them, lower "When idle" on AetherHub's Fading page (or
    /cb alpha);
    they still turn solid in combat or under your mouse.
  - Cooldown glow: the moment you use an ability, its button glows
    orange (for at least 2 seconds), turns blue, then blends through
    blue-green (aqua) to green as the cooldown runs down, and flares
    green when it's ready. Only the button you used lights up, not
    every button touched by the short pause after each cast. WoW
    Forever hides cooldown lengths, so the glow learns each one the
    first time you use it (it stays orange until ready that once); a
    spell with no real cooldown may flash orange briefly the first
    time, then never again.
  - Bag buttons get the same look, and other bars can match the size of
    Action Bar 1. With size matching on, the bag bar (with the
    keyring) and micro menu are also sized to Action Bar 1's height
    and spaced with the same gap. If they sit side by side they become
    one even strip. Micro buttons
    keep their narrower shape (squaring them would stretch the art) but
    get the same blue edge and dark socket. Changes wait out combat.
  - Align Bars: lining bars up by hand in Edit Mode is fiddly, so let
    AetherBars do it:
      1. Open Blizzard's Edit Mode and drag your bars ROUGHLY where you
         want them. They don't need to line up. Close Edit Mode.
      2. Click Align Bars on AetherHub's Layout page (it asks
         first), or type /cb align.
    What it does:
      - Everything lines up around Action Bar 1. Then the whole layout
        slides sideways to sit in the middle of the screen, keeping its
        shape. A bar off on its own, like a side bar at the screen's
        edge, stays put and doesn't count. (Untick "Center the bars on
        screen when aligning", or /cb align center off, to keep Action
        Bar 1 where you put it.)
      - Bars that sit roughly level form a row: their bottoms line up
        with an even gap between them.
      - Rows stack with matching left edges (or right edges or
        centers, whichever is closest to where you put them).
      - Every gap leaves room for each panel's border, glow and gold
        corners, so every bar keeps all four corners.
      - The bag bar, keyring and micro menu are one strip, lined up
        like any other bar. Align places the strip's buttons
        directly, so the extra space Blizzard's bag bar reserves
        (for the reagent bag slot) can't throw it off.
      - Bars clearly far from the rest (more than 3 buttons away) stay
        where they are.
    Undo Align (or /cb align undo) puts everything back exactly where
    it was. Moved a bar later? Just Align again.
    AetherBars keeps the new positions and puts them back the moment you
    log in or reload, before the loading screen lifts, so nothing jumps
    around afterwards (it moves each bar as a whole, so Blizzard's own re-
    layouts can't shift single buttons). The XP bar moves along with the
    bars, and if it would end up on top of a bar it's lifted to just above
    it. A bar off on its own, like a side bar at the screen's edge, is
    left to Blizzard, so the quest tracker keeps its usual place beside
    it. While Edit Mode is open, Align steps aside so you
    can drag bars. When you close it, your aligned layout comes right back
    unless you dragged a bar; if you did, your bars stay where you put
    them and you can click Align Bars to tidy them again. Bars never move
    during combat; if something needs fixing mid-fight, it waits until the
    fight ends.
    Tip: if Align puts a bar in the wrong row, nudge it more clearly
    above, below or beside its neighbor and Align again.
  - Tip: to move or resize the XP bar, click Unlock to Move on
    AetherHub's Layout page (or /cb xp): drag the bar to move it, drag
    the handle at its bottom-right corner to resize it, then click
    Done beside it (or Lock).
    The bar inside (and its rested XP shading) resizes with it. The
    same spot also shows reputation or honor when you track those.
  - Commands: /cb alpha 0-1, edge 0-1, combat on|off, mouseover on|off,
    trim on|off, glow on|off, macro on|off, art on|off, size
    bar2|all|off, align, align undo, align center on|off, xp,
    xp width N, xp height N, xp reset, reset.

AetherCoords - coordinates and waypoints                  /mc and /way
  Shows where you are, and lets you mark spots on the map with notes.
  - Your coordinates under the minimap, in a navy pill with a fine blue
    edge (Shift-drag to move them). With AetherSkins' minimap they sit
    just under its bottom gold chevron, with the zone name and clock in
    a second pill below them.
  - On the world map: the coordinates under your cursor, and your own
    position in the top-right corner.
  - Waypoints: the Aether star (a gold star in a thin gold ring on a navy
    disc, with a soft, round pulsing glow) and your own note, on the
    world map and the minimap. Ones beyond the minimap's edge sit on its
    rim, pointing the way. Hover a star for its note and how many yards
    away it is.
    To add one:
      - double-click a spot on a zone map and type a note, or
      - type /way 26 42 Rok'Alim (uses the map you have open, or your
        zone), or /way Thousand Needles 26 42 Rok'Alim.
    To remove one: right-click its star, or /way remove 2. /way list
    shows them all and /way clear removes them all.
  - Tip: when a guide gives you coordinates, paste them into /way so you
    can follow the star on your minimap.
  - Commands: /mc decimals 0-2, minimap on|off, popup on|off, reset.

AetherPathfinder - service NPCs on your maps                   /pfm
  Puts trainers, vendors, flight masters, mailboxes and other service
  NPCs on the world map and the minimap, so you can find them quickly.
  - Click the NPCs button in the top-left corner of the world map to
    choose what to show: class trainer, class pet trainer, stable
    master, general goods, ammo, food, innkeeper, flight master,
    mailbox, repair, profession trainers, other class trainers, bank,
    auction house and profession supplies.
  - Each marker shows an icon inside a ring in its category's color:
    WoW's own town icons (flight master, innkeeper, mailbox, bank and
    so on), your class's crest for class trainers, and the
    profession's icon for profession trainers. If WoW is missing an
    icon, that marker is a plain colored dot instead.
  - On the world map, quest markers ("!", "?" and objectives) always
    stay on top of these icons, so an NPC icon never hides a quest.
  - Class trainers follow your character's class. The class pet trainer
    is the Pet Trainer for hunters, Demon Trainer for warlocks and
    Portal Trainer for mages.
  - Hover a marker for the NPC's name, title and coordinates. Markers
    under your character's arrow turn see-through so you can still see
    yourself.
  - Flight masters you haven't discovered yet have a red ring and
    blink. Open the flight map at any flight master once on each
    character and the ones you already know stop blinking.
  - About 1,550 NPCs and 55 mailboxes are built in. It also learns every
    NPC you talk to and every mailbox you open, including ones in new
    WoW Forever areas.
  - Tip: the minimap markers follow you as you move, so you can walk
    straight to the nearest innkeeper or mailbox.
  - Commands: /pfm stats, /pfm flights (what the last flight map
    reported), /pfm debug, /pfm clearzone, /pfm reset.

AetherMarks - quest and rare mob highlights                    /qm
  Colors the names of mobs that matter to you.
  - Baby blue: mobs you still need for a quest, for kills or for items
    they drop. The color clears as soon as that objective is done, even
    before you turn the quest in.
  - Purple (like epic items): named quest mobs, the one-of-a-kind ones
    a quest asks for, like "Hogger slain: 0/1", or a single item that
    only that named mob drops ("Fang of Ishamuhale: 0/1"). A single
    item that ordinary mobs drop keeps them baby blue.
  - Orange (like legendary items): rare mobs. The first time you meet
    each rare, a sound plays and an alert shows on screen.
  - The colors show on your target, target-of-target and focus frames,
    and at the top of the tooltip when you mouse over a mob.
  - Rare Radar (on by default): press V once to turn enemy nameplates
    on, and every mob near you is checked the moment it comes in range,
    without targeting it. A rare gets a pulsing orange beacon over its
    head with a skull, its name in big orange letters, and RARE or RARE
    ELITE with its level, and the edges of your screen pulse orange
    with a sound.
  - With Rare Radar on, Blizzard's nameplates are hidden. Ordinary mobs
    show just their name, and quest mobs show it in their quest color.
    Quest colors work at any distance: mobs a quest says to kill are
    matched by name from your quest log right away. For "collect an
    item" quests, mouse over or target one mob of that kind once (or
    get close to one) and every mob of that kind lights up from afar,
    in this and future sessions. Mob types are remembered by both
    their creature ID and their name, so they still match in combat
    or far away, when the game hides one of the two. Every nameplate
    is checked again every 2 seconds, so a mob the game couldn't
    describe the moment it appeared still gets its color.
    Names keep the same size and brightness at any distance.
    Your target's name always shows, with a slim health bar under it
    and a slim cast bar (with the spell's name) while it casts.
  - Rare Radar raises the nameplate range to the most the game allows,
    so rares are found from farther away. Turning it off puts your old
    range and Blizzard's nameplates back. Inside dungeons Blizzard keeps
    its own nameplates, so Rare Radar only works in the open world.
  - Tip: without nameplates, mouse over or target a mob to see its
    color; the names the game draws over mobs' heads can't be recolored.
  - Commands: /qm quest, /qm rare, /qm sound, /qm radar (each turns
    that on or off), /qm names 50 (how visible ordinary mobs'
    names are with Rare Radar, 0 hides them), /qm debug (lists every
    nameplate on screen and why it got its color, handy for reports).

AetherItemID - item details                                    /itemid
  Hover an item in your bags or bank for a second and a small window
  opens next to its tooltip, placed so it never sits under your cursor.
  - Quests: which quests in your log need it, with your progress, and
    whether it starts a quest. A quest item that no quest in your log
    needs says "safe to discard" in red.
  - Crafting: which professions use it. For your own professions it
    lists the recipes, the ones you know in green.
  - Whether it's soulbound (in orange), how many you have in your bags
    and bank, and what a vendor pays for it.
  - Tip: open each of your profession windows once so it learns your
    recipes, and open your bank once per session for exact bank counts.
  - Commands: /itemid on|off, /itemid delay 1 (seconds to hover),
    /itemid reset, /itemid debug.

AetherLedger - where to quest, train and skin next             /ledger
  Knows which quests you've done and which are in your log, and works
  out which ones you could pick up right now: near your level, right
  for your race, class and faction, with any earlier quests in the
  chain already done.
  - Better zone: when another zone has clearly more of those quests
    than the one you're in, a small window lists your best zones to
    pick from, for example "Desolace: 7 quests (33-35), 2 chains, 2 in
    your log", each with a Go button. The same window also mentions
    rank-ups due, new class or profession quests, and quests that
    turned gray. A single new class or profession quest gets its own
    Go button too. Show quests opens the full list in AetherHub, Clean
    up opens the gray-quest window, and Not now closes it. Check zones
    now always starts with your own zone (its quests at your level, or
    that it has run dry), then your best other zones, and says when
    yours is still the best. Drag the window (or the cleanup or
    directions window) where you like it and it opens there from then
    on; /ledger resetwindows puts them back. Chains that
    keep going past your level count extra, so you can stay in one
    zone longer.
  - Go: puts a waypoint (AetherCoords) on that zone's quest giver with
    the most of your quests, and opens a small directions window:
    the zeppelin or boat to take, the flight master to fly from (one
    whose path you know, from AetherPathfinder), and the walk at the
    end with yards and direction. Steps tick off with a green check as
    you go, and on the flight map your stop glows green. The window
    widens to fit its steps; a very long step wraps under itself, and
    the title stays on one line. Like AetherMeter, it fades to
    the meter's transparency when you're not using it, and turns solid
    while your mouse is over it, and for a few seconds when you click
    it or a step is done. When you
    click the quest giver (or walk right up to them), "You're there!"
    and their name flash in big letters in the upper middle of the
    screen, the waypoint comes off your map and the window closes. Its
    x closes it early (the waypoint stays).
  - Quest givers on the move (61 quests, like Cork and Rigger
    Gizelton's caravan in Desolace) say "on the move" in the lists
    and the directions window. The walk aims at the nearest point of
    their road, and reaching the road counts as there ("You're on the
    road!"): look along it for them.
  - Professions: when a profession is near its cap (Skinning 147/150),
    it tells you which rank to train and the nearest trainer who
    teaches it. Expert and Artisan crafting are only taught by some
    trainers ("Artisan" and "Master" titles), and for Cooking, First
    Aid and Fishing those ranks come from a book or quest.
  - Quest tracker: the objectives list on your screen follows where you
    are. In a zone it shows that zone's quests, lowest level at the top,
    plus quests ready to hand in there (a finished quest shows up in the
    zone where you turn it in, not where you got it). Red quests (too hard
    for now) are left out until a level-up turns them orange; when one
    you just accepted goes, a chat line says why.
  - Finished quests from any zone that are handed in somewhere else
    stay at the bottom of the list, under a thin gold line (clear of
    the first one's title), reading "Ready for turn-in: Orgrimmar"
    (the zone to go to).
    The zone comes from the game's own turn-in marker first, so quests
    the guide doesn't know about show up there too.
  - Somewhere with nothing for you (a city, a road), it shows the
    quests of the zone you're heading to with Go, or else the zone
    holding most of your quests. A line in chat says which zone the
    list is following whenever that changes.
  - It switches after you've been in a new zone for 5 seconds (no
    flicker along borders), and waits while you're flying or fighting.
    Quests you track yourself (shift-click in the quest log) stay
    pinned in every zone until you untrack or finish them; quests you
    untrack stay hidden. A quest that's ready to hand in shows even if
    it was red, since there's nothing left to fight. If WoW adds a quest
    to the tracker on its own (it does when you make progress), Ledger
    puts the list back a second later.
  - The tracker's Aether look: Blizzard's "All Objectives" bar is
    gone (each section keeps its own fold; its space stays, so move the
    tracker up in Edit Mode if you like). Section headers like
    "Quests" get a navy band that fades to the right, gold lettering,
    a gold line that tapers at both ends and a plain gold - / +. Quest
    icons become a navy disc with a gold ring: gold dots while you're
    working on it, a gold ? when it's ready (a soft gold glow marks
    the quest you're following). Yellow quest names turn Aether gold
    (other difficulty colors stay), "Ready for turn-in" is Aether blue,
    the text uses the Aether font, and a soft blue band shows behind the
    quest you point at. A quest you accept zooms onto the list (its
    icon starts about a third of the screen across and shrinks into
    place), and one you hand in swells and fades off, half a second
    each. Turn it off on AetherHub's AetherLedger tab (takes effect
    after a reload).
  - /ledger tracker lists every quest in your log with its color, zone
    and why it is or isn't on the tracker.
  - Tooltips: ones the game puts in its usual corner (bottom right,
    over AetherMeter) show just left of the quest tracker instead,
    centered at mid-screen. Move the tracker in Edit Mode and they
    follow it (if it's near the left edge, they go on its right).
    Tooltips placed by your mouse or beside a button or bag stay put.
    /ledger tooltip switches back to the corner, or on again.
  - Gray quests: when quests in your log turn gray (little XP now),
    you're told once, and Clean up opens a small window listing them,
    each with an Abandon button (click once, then again on "Sure?").
    Nothing is dropped without your click. Gray quests that are ready
    to turn in are listed as worth turning in instead, and class and
    profession quests, or ones that lead on to quests at your level,
    are left out.
  - Class and profession quests you can take are listed on their own
    (they don't count toward a zone), and you're told about new ones.
  - Skinning: lists zones with beasts close to the highest level you
    can skin (skill / 5, or skill / 10 + 10 below 100), where skill-ups
    come fastest. Beasts are picked by name (wolves, cats, raptors,
    basilisks and so on), so a few odd ones may be missing.
  - Pick what you want on AetherHub's AetherLedger tab. Each message
    shows once (a zone once per level); it waits until combat ends and
    stays quiet in dungeons. Checks run only when something changes:
    you level up, gain skill, accept or turn in a quest, or change zone.
  - It also saves your quest log and completed quests to a file you
    can share: type /ledger (or click Save Quest Log to File), then
    /reload
    or log out. WoW writes the file to:
      _forever_\WTF\Account\<account>\SavedVariables\AetherLedger.lua
    It records automatically when you log in and out too, and opens
    any collapsed zone headers in your quest log to see every quest.
  - Quest data comes from QuestieDB. WoW Forever's brand-new quests
    aren't in it yet, so they aren't suggested (they still count once
    they're in your log). Zeppelin and boat docks are built in for the
    classic routes.
  - Commands: /ledger zones (everything above, in chat), /ledger check
    (check now and show the window), /ledger go and /ledger stop
    (directions), /ledger suggest (on or off), /ledger cleanup (gray
    quests to drop), /ledger sort (re-sort the quest tracker), /ledger
    tracker, /ledger tooltip (tooltip spot), /ledger (record now),
    /ledger status.

AetherPack - your bags, sorted into sections                    /pack
  Everything in your bags in one compact window, sorted into sections.
  This includes the reagent bag in WoW Forever's fifth bag slot (or a
  warlock's soul bag, if that's what sits there):
    Ammo         arrows and bullets, plus everything in your quiver or
                 ammo pouch (for other classes this is Soul shards or
                 Class reagents, see below)
    Quest items  anything a quest needs
    Gear         weapons and armor, best quality first
    Consumables  food, drink, potions, bandages, scrolls
    Trade goods  leather, cloth, herbs, ore, recipes and other crafting
                 materials
    Other        hearthstone, keys, bags and the rest
    Junk         gray items, with their total vendor value
    Free slots   your empty slots (folded; or use the deposit slot)
  - Each item sits in a thin frame in its quality color (green, blue,
    purple and up); everything else gets Aether blue.
  - What's left, as short colored words beside the deposit slot's
    lettering (under it in a narrow window). Hover a line for the full
    numbers.
      Bags      free slots: green with room to spare, Aether gold in
                the last quarter, red when nearly full ("Full" at 0)
      Reagent   your reagent bag's free slots, colored the same way
                (shown when you have one equipped)
      Ammo      a white count. At half a full quiver or ammo pouch
                (or less), "Warning" in Aether gold comes before it;
                at 300 or less, a red "Low" that pulses until you
                restock. With no quiver: the count, then Low at 300.
      Shards    your soul shard count (warlocks); a pulsing red "Low"
                under 3
    Under them, Reagents lists your class reagents and how many (mage
    runes and powder, priest candles and feathers, shaman ankhs,
    paladin symbols, druid seeds and herbs, rogue powders, warlock
    stones); red at 2 or less.
  - A folded section shows "Show" at the end of its line (Free slots:
    "Show empty").
  - No swaps. Just drops.: a row of its own under the last section
    (right under Free slots when that's folded), lined up with the
    first column of items: a slot like your item slots with an amber
    rim and a soft glow that falls into a dark middle, and "NO SWAPS.
    JUST DROPS." chalked beside it with an arrow curving into it. Drop an
    item on it (or click it while holding one) and it goes into a free
    slot. Nothing already in your bags gets moved or swapped, so a drop
    can't land on another item by accident. Crafting reagents go to
    your reagent bag first, ammo to your quiver (and shards to a soul
    bag); everything else to your first regular bag with room. The
    number in it is your free regular slots; it pulses gently while
    you hold an item (/pack pulse item|always|off). The rim and glow
    turn red when you're full, and a drop then just tells you there's
    no room. /pack deposit off hides it. (The lettering is drawn with
    the Amatic SC font, SIL Open Font License.)
  - Your free bag slots also show as a small number on the backpack
    button, so you can check without opening anything.
  - B (or any key you've bound to your bags) and the backpack button
    open AetherPack instead of Blizzard's bags (including Blizzard's
    combined backpack window). Press the key again to close it, along
    with any single-bag windows.
  - Click one bag on the bag bar (one of the four bag slots or the
    reagent bag) to open a small window with just that bag, in slot
    order, with the bag's name and its used/total slots in the title
    (the window widens to fit a long name). Blizzard's own window for
    that bag stays closed, the reagent bag's included.
    Click the bag again, its x, or Esc to close it. Open as many as
    you like: they stack up from the lower right, a new column to the
    left when one gets too tall. Drag one and it stays put. A Toggle
    Bag 1-4 key opens the same windows. In a fight, a bag window you
    haven't opened yet this session opens when combat ends.
    Turn all this off on AetherPack's AetherHub tab, and /pack still
    opens the combined window.
  - Click a section's title to fold or open it; it stays that way.
    Empty sections hide themselves.
  - Type in the search box to dim everything that doesn't match.
  - Items you just picked up glow until you hover them, like in
    Blizzard's bags.
  - Right-click to use, equip, drink or sell, just like normal bags,
    and hovering an item still opens AetherItemID's window.
  - At a vendor, the Sell junk button sells every gray item (and
    nothing else).
  - Your gold sits in a capsule next to the title, each number in its
    coin's color. Hover it to see what you've gained or lost this
    session and your gold per hour (shown after 10 minutes). The
    session starts when you log in or reload.
  - Drag the window by its edge to move it; it remembers the spot.
  - WoW doesn't let addons rearrange bag buttons during a fight, so
    the sections catch up when combat ends. Items still work.
  - Commands: /pack (open or close), /pack replace on|off, /pack count
    on|off (backpack number), /pack deposit on|off, /pack pulse
    item|always|off, /pack columns 6-16,
    /pack scale 0.6-1.5, /pack reset (all window positions).


AetherChat - chat that fits beside your bars                   /achat
  Blizzard's chat window with the Aether look. Chat itself is still
  Blizzard's: tabs, channels, colors and filters work as before
  (right-click a tab for its settings).
  - Fits the gap: chat fills the space between the left edge of your
    screen and your action bars, as tall as the main block of bars (a bar
    off on its own, like a side bar at the screen's edge, doesn't count),
    with the same small gap as between the bars. A docked AetherMeter
    mirrors it on the right. It follows the bars when you Align them.
    (Needs AetherBars with its Aether trim on; otherwise chat stays where
    Blizzard puts it.)
  - Aether panel: the same frame as the bars (AetherMeter's colors and
    see-through level, blue frame, gold corners), with a thin line
    under the tabs. The tab strip is compact: no empty band above the
    tab names, so there's room for more chat. It turns solid while your
    mouse is over the chat or you're typing, and fades back when you
    stop. The text itself always stays fully readable.
  - Smaller text: starts one size smaller than Blizzard's; set it with
    "Chat text" on AetherHub's Appearance page.
  - Less clutter: Blizzard's chat background, the voice, channel and
    emote buttons, and the tab art are gone. Tabs are flat, the tab
    you're on has its name in Aether gold with a gold underline, and the
    others are a dimmer gold. Channels and emotes still work by
    typing (/join, /dance).
  - Slim typing line: press Enter and a thin line appears over the
    bottom of the chat; it disappears when you send or press Escape. It
    stays hidden the rest of the time, even if Blizzard tries to show it
    (the "Classic" chat style keeps it up), so it never covers the
    newest line.
  - Tip: chat no longer fits? Make sure there's at least about 220 wide
    by 90 tall beside your bars, then click Fit Chat Now (Layout page).
  - The text and tabs start just inside the panel's left edge (Blizzard
    normally keeps chat windows a little way in from the screen's edge;
    the fitted chat doesn't). If the text still sits too far right, type
    /achat inset 10 (or another number) to pull it left, and /achat
    inset alone to undo that.
  - Commands: /achat fit on|off, now, font 8-24, trim on|off, buttons
    on|off, edit on|off, inset N, debug (shows where things sit),
    reset.


AetherFrames - player, pet, target and party frames            /af
  Replaces Blizzard's player, pet, target and party frames with the Aether
  look. They work the same way: click a frame to target, right-click
  for its menu.
  - Round crest: the live portrait inside a thin gold ring and a blue
    ring, with beveled gold chevrons (with a fine echo) pointing outward
    at 12, 3 and 9 o'clock.
  - Class medallion at 3 o'clock, where the crest meets the capsule:
    for player characters (you, and players you target), a small dark
    medallion with a fine gold rim and a gold class glyph. The glyphs
    are original Aether designs: a bow (hunter), a star with sparks
    (mage), a sword (warrior), a curved dagger (rogue), a sun (priest),
    a hammer (paladin), a leaf (druid), a lightning bolt (shaman) and a
    flame (warlock). Non-player targets keep the chevron there. Party
    members get one too, a little smaller.
  - Level badge at 6 o'clock: a round badge with the level in it. Yours
    is gold. The target's takes its difficulty color, like Blizzard's:
    red (5 or more levels above you), orange (3-4 above), Aether gold
    (within 2), green (lower, still worth experience), gray (too low).
    A + means elite. ?? (far too high to tell, or a boss) gets its own
    look: a thick red ring around a black center. Every badge shows
    its number in white with a black outline, so it reads on any color.
  - Your pet's crest: its level in a gold badge at 6 o'clock, and its
    happiness (hunters) in the medallion spot at 3 o'clock: a
    gold smiley when happy, a blue straight face when content, a red
    frown when unhappy. It reads happiness the way WoW Forever
    provides it (C_PetInfo), and checks once a second.
  - Capsule: your name and level, health and mana (or rage, energy,
    focus) slide out from behind the crest in a rounded capsule. The
    capsule, the bars and the gold line under the name are cut to
    follow the ring's curve on one side and the capsule's rounded end
    on the other. A thin outline traces each bar's shape, so it looks
    the same full, empty, or when you're dead or a ghost, and the fill
    sweeps across both curves. All the round shapes are smooth images
    (in the Media folder), so edges stay clean at any frame size.
    Numbers have a dark outline so they read clearly over any bar
    color. Names and levels use Fira Sans Bold (included, under the
    SIL Open Font License), heavier than WoW's own font so they stand
    out.
  - Your pet's frame sits below yours with health numbers and a thin
    resource bar (no number unless you turn it on; handy for
    warlocks).
  - Hawk and totem timers: Blizzard's strip with Summon Hawk's hawks
    (and totems and other temporary helpers), each with its time left,
    sits under your crest, between your frame and your pet's. It's
    Blizzard's own, so tooltips and right-click dismiss work as usual.
  - Party frames: your party members in small crests (the size of your
    pet's), stacked down the left side, starting where Blizzard's party
    frames were. Each has health and mana (or rage, energy) with numbers,
    a gold level badge, the class medallion, and the threat glow when a
    mob is on them. Up to 4 of each member's debuffs sit to the right of
    the capsule, each edged in its type's color (magic, curse, poison,
    disease), so you can see what you're able to remove. Members out of
    range (about 40 yards) fade to half; offline members turn gray and say
    Offline. Click to target, right-click for the menu. Drag them with
    Unlock to Move on AetherHub's Layout page (they move as one). Untick
    "Party frames in the Aether look" (or /af party off, then /reload) to
    get Blizzard's party frames back.
  - Target of target: who your target is targeting, in a small crest
    the same size and shape as your pet's frame, mirrored like the
    target frame, under the target's buff and debuff row. Health with
    numbers, a thin resource bar (no numbers), the level badge and the
    class medallion. No threat glow (that's for your own threat).
    Click it to target that unit. Drag it with Unlock to Move. To turn
    it off: /af tot off, then /reload.
  - Your buffs and debuffs stay top right, where Blizzard shows them.
    The target gets a row under its frame: its debuffs (yours
    included, red edge) first, then its buffs (blue edge), each with
    its time left underneath (up to 9; hover one for its tooltip).
    Want your own buffs in your frame too? Tick "Your own buffs in
    your frame too" (or /af mybuffs on).
  - Aura rows keep working in combat. WoW Forever hides auras from
    addons during a fight (when most debuffs land), so these rows use
    Blizzard's own aura display (AuraContainer), which the game fills
    in itself: icon, stack count and time left. The look is still
    Aether's. Auras with no end (like Aspect of the Hawk) show no timer.
  - The aura rows and the hawk/totem strip sit snug under the capsule
    (about 6 px below it on a typical screen).
  - The target frame is the mirror image on the other side: its name
    is red for enemies and Aether gold for neutral, and its health and
    power drain toward the crest (a mob with no mana or rage shows an
    empty bar). Its capsule is the same height as yours. Elite targets
    get a + after their level. A mob someone else tagged first (no
    credit or loot for you) turns gray, like on Blizzard's frame: gray
    name and health bar, and a dimmed flat portrait.
  - Threat glow: a wide, soft Aether-blue halo around the portrait. How it
    moves says how urgent it is; steady means fine, moving means act.
    On your frame and the target's: nothing while your threat is low,
    a slow pulse when you reach 80% of the tank's threat (if the game
    tells addons), a fast pulse when you've passed it and the next hit
    may come your way, and solid when it's attacking you. On your
    pet's frame: a dim steady glow while your pet holds aggro, and a
    fast pulse when it's losing it. If the game hides threat from
    addons in a fight, the glow simply stays off.
  - Portraits: live 3D models on a soft glow in Aether blue, brightest
    in the middle and fading to navy at the gold ring, so dark pets and
    targets (a black wolf, say) stand out. Your pet's camera sits a bit
    farther back so more of the glow shows. Where the game won't give a
    model (a unit out of sight, some units in dungeons and raids, or an
    offline party member, shown in gray), the frame uses the game's
    flat portrait, with its black background, instead. /af portraits
    2d switches to the flat portraits everywhere; /af portraits 3d
    brings the models back. /af portraits test shows models on every
    frame with no fallbacks (until /reload), and /af auras lists each
    portrait and why it's flat, for tracking down problems.
    To fit the 3D faces: /af portraits zoom 1.3 (bigger number = camera
    farther back, smaller face) and /af portraits shift 0 -2 (moves the
    model: right/left, then up/down). Put pet, player, target, tot or
    party first to change just those frames (/af portraits zoom pet
    1.5). /af portraits tune shows the settings; /af portraits tune
    reset puts the starting ones back.
  - Portrait colors: the glow behind a portrait is shaded, the color
    itself in the middle and darker at the rim. An enemy mob as your
    target gets the color of its level badge (gray, green, gold, orange
    or red; red for "??"). Player characters (friendly or not) and
    friendly NPCs get their class color, the game's own, on your target,
    the target of target and the party frames. You (even as your own
    target) and your pet always keep the Aether blue. /af levelglow off
    and /af classglow off turn either back to blue.
  - Fading: out of combat the rings, capsules and bars fade to the
    level you choose (50% to start); names, numbers and faces stay
    solid (tick "Faces fade too" to fade the portraits as well).
    Everything turns solid under your mouse; in combat, see Aggro
    fading below.
  - Aggro fading: in combat, only your target, the target of target and
    whoever has aggro on your target (you, your pet or a party member)
    stay solid. Whoever your target is attacking lights up at once.
    Everyone else fades further than out of combat: the frame to 20%, the
    bars to 35% (they carry your health), and the portrait to 20% over a
    dark disc, so the lit frame stands out. If your own frame lights up
    while your pet tanks, you've pulled. Names and numbers never fade. /af
    combatalpha 0-1 sets the in-combat level; /af aggro off makes every
    frame solid in combat again. The bars never fade below 35%, in or out
    of combat.
  - Hit flash: when you, your pet or a party member takes a hit, that
    crest's ring and the glow around it flash red: full red for a tenth of
    a second, then gone within about a third of a second (misses, dodges
    and parries don't flash; your target never does). Damage over time
    flashes with each tick. /af hits off turns it off. /af hitnumbers on
    also floats the damage up over the portrait for a moment, bigger for
    crits (off to start).
  - Placement: the first time, the frames go where Blizzard's sat. Click
    Unlock to Move on AetherHub's Layout page and drag any frame: yours,
    your pet's, your target's, target of target and the party's each
    move on their own (your pet's follows yours until you move it).
    While moving, every frame shows, even with no pet, target or party;
    empty ones show empty bars. Click Done on any frame, or right-click
    it, to finish. A /reload always comes back locked. Reset Pet Frame
    Position puts your pet's frame back below yours. Frames can't be
    moved during combat.
  - Line up after moving: when you finish (Done, right-click or Lock)
    and you moved your frame, your pet's, the target's or the target
    of target, a small box asks "Line up your frames?":
      Line Up: your frame stays put; the target levels with it; your
        pet's capsule end lines up under yours and the target of
        target's under the target's, with those two level. Edges land
        on whole screen pixels. A frame you parked somewhere else (more
        than about 20 units out of line) is left where it is.
      Line Up and Center: the same, then the lined-up group slides
        sideways into the middle of the screen, keeping its shape and
        its height.
      Keep As Is (or Escape): every frame stays exactly where you
        dropped it.
    Moving only the party frames doesn't ask. The same two line-ups
    are on AetherHub's Layout page any time, or /af lineup and
    /af lineup center.
  - Centered: your frame and your target's sit side by side in the
    middle of the screen, mirrored, with your pet's under yours and the
    target of target under the target's. Their inner ends line up, each
    row is level, and the edges land on whole screen pixels for crisp
    lines. This happens once, on your first login with 1.7.0; after
    that the frames stay where you put them. To center them again,
    type /af center (your frame keeps its height, so drag it up or
    down first if you like).
  - Not shown yet: combo points (rogues, druids) and the small leader,
    PvP and resting icons. If you need those, turn AetherFrames off for
    now.
  - Turning it off brings Blizzard's frames back after a /reload.
  - Commands: /af alpha 0-1, faces on|off, buffs on|off, threat on|off,
    mybuffs on|off, aggro on|off, combatalpha 0-1, hits on|off, hitnumbers
    on|off, levelglow on|off, classglow on|off, party on|off, tot on|off,
    petpower on|off, scale 0.6-1.6, portraits 3d|2d, unlock, lock, lineup
    [center], center, petreset, reset, on|off, auras (a report of what the
    game tells the addon about your auras and hawk timers, for tracking
    down problems).


AetherSkins - the Aether look for Blizzard's windows           /skins
  Gives Blizzard's own windows and the minimap the Aether look.

  Windows (Character and Reputation, Friends, Talents, Progress Track,
  and every other window built on Blizzard's standard frame):
  - The Aether frame: rounded dark panel, blue edge, soft blue glow,
    navy title strip with a gold underline and gold title, the four
    gold chevrons, and a plain navy crest behind the portrait.
  - Inside: navy buttons with white text, dark checkboxes with a gold
    check, blue scroll bars, navy tabs (gold edge on the open one),
    and dark search boxes.
  - Blizzard's yellow text is Aether gold everywhere (the only yellow).
  - Blizzard's own art is only faded out, never removed or moved, so
    every window works as before. A window opened in combat gets the
    look right after the fight.
  - A window that was missed: point at it and type /skins this, and
    send /skins debug so it can be added for good.

  Forever's own window parts (second pass):
  - Side tabs (Character, Friends, Progress Track): navy, with a gold
    edge and a gold notch on the open one. Windows with side tabs drop
    the right-hand chevron.
  - List headers (Reputation, Friends, the quest log) are navy strips
    with gold names, also after you fold or open them. Rows that
    appear as you scroll get the look right away. Reputation and
    standing bars are dark capsules that fit around the fill
    (Neutral in Aether gold, Friendly and up in Aether green); the
    picked row is blue; brown backgrounds are gone, bronze lines blue.
  - Friends: navy friend cards (offline ones dimmer), the picked one
    blue. They stay that way when the game recolors them.
  - Dark text meant for parchment (spell names and ranks, page
    headings, gossip and quest text) is light on the navy pages.
  - Character: gear slots lose Blizzard's bronze frame; each has a
    thin frame in the item's quality color (blue for plain items),
    the stat tabs are navy and the zoom and turn buttons gold on
    navy. Vendors' items get the same quality frames.
  - Talents: spec icons gold on navy. Maxed talents are tinted gold
    with a gold frame; talents with some points have a blue frame;
    talents you can take now glow blue; ones you can't take for lack
    of points are light navy on a faint navy plate; locked ones are
    light gray (none are darkened any more). Each taken talent shows
    a pill such as "2 of 5" on its bottom edge, and the arrows between
    talents are thicker and 3D (gold, blue or gray, like their talent;
    the gray ones solid).
  - Spellbook: the same scheme. Known spells have a thin blue frame in
    place of Blizzard's ornate ones (blue, and brown for passives),
    ones you can learn at a trainer now glow blue with
    a "Trainer" pill, ones above your level are navy with their level
    in a pill, and the category tabs are gold on navy.
  - Group Finder (I): the tank, healer, damage and New Player Friendly
    buttons are gold symbols on a navy disc (all the same size) with a
    blue ring that turns gold when you pick it. Red close buttons
    anywhere in a window get the navy Aether one.
  - World map: the Aether frame and buttons, a navy zone bar with blue
    edges, and the quest log beside the map in navy with gold zone
    headers.
  - Progress Track: navy reward cards and a gold progress bar.
  - Vendors: navy item tiles (only where there's an item), navy repair
    and junk buttons, and Merchant / Buyback tabs that line up.

  The minimap:
  - Blizzard's ring around the minimap is replaced by a navy ring with a
    bevel (a ridge along its middle), the four gold chevrons at 12, 3, 6
    and 9 o'clock (beveled too, lit from the sun's side), and a soft
    blue glow around it.
  - The ring is plain navy all the way around, day and night, with no
    glow from the sun or moon. The map itself isn't tinted.
  - The sun or moon button is the Aether one: a navy button with a gold
    sun by day and a pale moon at night. Hover it for the game time;
    click it for the calendar (it replaces the calendar button).
  - The tracking magnifier sits on the ring across from the sun, on the
    same navy button, as a flat magnifier in Aether blue. Click it for
    the tracking menu as before.
  - Under the minimap: your coordinates (AetherCoords) just under the
    bottom chevron, then a navy pill with the zone name and the clock.
    A yellow zone name turns Aether gold; other zone colors (friendly,
    hostile, contested) stay. The clock and zone name work as before,
    and the mail icon sits just left of the pill.
  - Hidden: the calendar button (the sun opens it), the addon button
    with the "1" (AetherHub's own button is on the ring), and Forever's
    own coordinates under the minimap (the Aether pill shows them).
  - The map, its pins, AetherCoords' waypoints, AetherPathfinder's NPCs
    and other addons' minimap buttons all work as before.
  - Commands: /skins minimap and /skins windows (each on or off, then
    /reload), /skins this, /skins day and /skins night to preview the
    sun or moon (/skins auto follows the game again), /skins debug
    (what it found and changed: send this if something looks off),
    /skins tree (point at a window: saves its structure for AetherHub's
    Debug page; up to 1,500 lines, with hidden parts folded into one
    line each). Both switches are also on the AetherSkins tab in
    AetherHub (/hub skins), and Debug Skins on its Debug tab.


AUTOMATIC NPC DATA REFRESH (optional, Windows only)
---------------------------------------------------
Keeps AetherPathfinder's built-in NPC locations up to date by
downloading the latest data now, then every day at 3:00 AM Mountain
Time (or as soon as the PC is back on). You keep starting WoW from
Battle.net as usual. It's set up once with a single command; Windows'
Smart App Control blocks downloaded scripts, but not commands you type
or paste yourself.

1. Press the Windows key + R. The Run box opens.
2. Paste this whole line into it (it's one line; copy all of it, from
   powershell.exe to pause") and press Enter:

powershell.exe -nop -ep bypass -c "$a='C:\Program Files (x86)\World of Warcraft\_forever_\Interface\AddOns';gci $a -r -i *.cmd,*.ps1|Unblock-File;& ($a+'\AetherPathfinder\Updater\Update-PathfinderData.ps1') -InstallSchedule;pause"

   If WoW isn't installed in C:\Program Files (x86)\World of Warcraft,
   change that part of the line to your folder before pasting.
3. A blue window opens and says "Automatic refresh is on", then
   "Updated AetherPathfinder data" (or "Already up to date"). Press any
   key to close it.

Run the same command again after installing a new version of the addons
(the command never changes; the Run box remembers it, so press Windows
key + R and pick it with the down arrow). To turn the refresh off,
double-click AddOns\AetherPathfinder\Updater\Remove-AutoRefresh.cmd, or
delete the task "AetherPathfinder Refresh" in Windows Task Scheduler.


GOOD TO KNOW
------------
- Every Aether window (AetherHub, AetherMeter, AetherLedger's windows,
  AetherPack, AetherItemID's item details, the waypoint note box and
  the confirm boxes) has its own look, so you can tell them apart from
  Blizzard's at a glance: rounded corners, a blue edge with a fine
  inner line, a soft Aether-blue glow (brightest at the edge, fading
  out over about 10 pixels), a navy title strip with a gold underline,
  and gold chevrons (thick, with a fine echo) pointing outward at 12,
  3, 6 and 9 o'clock, the side ones a little larger. Every gold chevron
  in the suite (windows, bars, the XP bar, the meter and the unit
  frames) is beveled, lit from the top-right like the minimap ring.
  When AetherMeter is docked beside your bars, it keeps only the top
  chevron. Buttons are navy with a blue edge. In AetherHub, gold means
  "on": a checked box fills gold with a gold edge, and slider handles
  are gold.
- If an addon ever seems to do nothing, type /console scriptErrors 1 and
  /reload. WoW hides addon errors by default; this shows them, and the
  error text pinpoints the problem.
- Settings are saved per character as well as account-wide, because WoW
  Forever has been reported to lose account-wide addon settings.
- AetherItemID used to be called AetherLens. If you still have an
  AetherLens folder in AddOns, delete it; your settings carried over.
- Upgrading from the very first names (CleanBars, MapCoords,
  PathfinderMap, QuarryMarks)? With WoW closed, double-click
  AddOns\AetherHub\Tools\Migrate-OldAddons.cmd once (run the setup
  command above first if Windows blocks it). It moves your settings to
  the new names and sets the old folders aside.
- Built-in data comes from QuestieDB
  (https://github.com/Questie/QuestieDB)
  for NPCs, mailboxes and quests, and from AtlasLootClassic
  (https://github.com/Hoizame/AtlasLootClassic) for recipes. See the
  DATA_NOTICE.txt files in AetherPathfinder, AetherItemID,
  AetherLedger and AetherMarks before sharing the addons publicly.
