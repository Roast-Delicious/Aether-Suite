# Release C, mockup 4: Map & Waypoints page in layout B.
import hub_layout as L
CATS = ['Class Trainer (Hunter)', 'Pet Trainer', 'Stable Master', 'General Goods', 'Ammo / Bows / Guns',
        'Food & Drink', 'Innkeeper', 'Flight Master', 'Mailbox', 'Repair', 'Profession Trainer',
        'Other Class Trainer', 'Banker', 'Auctioneer', 'Profession Supplies']
ON = {'Class Trainer (Hunter)', 'Pet Trainer', 'Stable Master', 'Ammo / Bows / Guns', 'Food & Drink',
      'Innkeeper', 'Flight Master', 'Mailbox', 'Repair', 'Profession Trainer'}

def page(p):
    p.title('Map & Waypoints', 'Coordinates, waypoints and NPCs on your maps')
    p.band('Coordinates', 'AetherCoords')
    p.check('Your coordinates under the minimap')
    p.check('Cursor coordinates on the world map')
    p.choice('Decimal places', ['45, 68', '45.2, 68.1', '45.23, 68.10'], '45.2, 68.1')
    p.band('Waypoints', 'AetherCoords')
    p.wplist([('Desolace', '67.0, 58.2', 'Cork Gizelton'), ('Thousand Needles', '26.0, 42.0', ''),
              ('The Barrens', '51.5, 30.3', 'Crossroads FM')], new=True)
    p.note('Double-click a zone map to add one, or type /way 26 42 note.')
    p.buttons(['!Clear All Waypoints...'])
    p.band('NPCs on your maps', 'AetherPathfinder')
    p.dropdown('Class trainers for:', 'Auto (Hunter)')
    for i in range(0, len(CATS), 2):
        a = CATS[i]; p.check(a, on=a in ON, ux=0, row_end=(i + 1 >= len(CATS)))
        if i + 1 < len(CATS): b = CATS[i + 1]; p.check(b, on=b in ON, ux=210)
    p.buttons(['Show All NPC Types', 'Hide All NPC Types'])
    p.check('Built-in NPC locations', ux=0, row_end=False); p.check('Other faction\'s NPCs', on=False, ux=210)
    p.check('Markers on the minimap too')
    p.band('Learned NPCs', 'AetherPathfinder')
    p.note('412 NPCs learned across 23 maps (every NPC you talk to is added).')
    p.buttons(['!Clear NPCs in This Zone...', '!Clear All Learned NPCs...'])
    p.gap(4)
    p.buttons(['!Restore Defaults...'])

L.render_b('Map & Waypoints', page, 'out_hub_map')
