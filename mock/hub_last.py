# Release C, mockups 8 + 9: Your Character and Help & Debug in layout B.
import hub_layout as L
L.NO_MM = True
def me(p):
    p.title('Your Character', 'Read from the game, always up to date')
    p.note('Jay Iscariot, level 36 Troll Hunter (Horde)', 16)
    p.band('Professions')
    p.lines([('Leatherworking  165 / 225 (Expert)', ''), ('Skinning  247 / 300 (Artisan)', ''),
             ('First Aid  225 / 225 (Expert)', 'train Artisan now'), ('Cooking  99 / 150 (Journeyman)', ''),
             ('Fishing  20 / 75 (Apprentice)', '')])
    p.note('Quests & Mobs uses this for its suggestions; Map & Waypoints\' class trainers follow your class.')
VERS = [('AetherHub', '1.14.8'), ('AetherBars', '1.14.3'), ('AetherChat', '1.0.8'), ('AetherCoords', '1.3.15'),
        ('AetherFrames', '1.14.7'), ('AetherItemID', '1.1.4'), ('AetherLedger', '1.8.7'), ('AetherMarks', '1.6.13'),
        ('AetherMeter', '1.13.9'), ('AetherPack', '1.6.4'), ('AetherPathfinder', '1.9.6'), ('AetherSkins', '1.5.7')]
def debug(p):
    p.title('Help & Debug', 'Versions and reports, ready to copy')
    p.band('Versions')
    p.lines(VERS, cols=2)
    p.band('Reports')
    p.rowbuttons('Report:', ['Bars', 'Chat', 'ItemID', 'Marks', 'Pathfinder', 'Skins', 'Ledger'])
    p.rowbuttons('Ledger:', ['Zones', 'Tracker'])
    p.rowbuttons('Pathfinder:', ['NPC Counts', 'Flight Paths'])
    p.buttons(['Check Memory', 'Show Window Dump'])
    p.check('ItemID: explain in chat what it finds while you hover', on=False, new=True)
    p.note('Window dump: point at a window, type /skins tree, then Show Window Dump.')
    p.band('Output')
    p.box(['== Memory ==', 'AetherHub            405 KB', 'AetherBars          1517 KB', 'AetherLedger        3152 KB',
           'Total               9693 KB', '(Ctrl+A, then Ctrl+C to copy)'], 130)
    p.buttons(['Copy Full Report', 'Clear'])
L.render_b('Your Character', me, 'out_hub_me')
L.render_b('Help & Debug', debug, 'out_hub_debug')
