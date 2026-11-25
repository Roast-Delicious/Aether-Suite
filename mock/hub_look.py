# Release C, mockup 7: Window Look page in layout B.
import hub_layout as L
L.NO_MM = True
def page(p):
    p.title('Window Look', 'The Aether look for Blizzard\'s windows and the minimap')
    p.band('Blizzard\'s windows', 'AetherSkins')
    p.check('Blizzard\'s windows in the Aether look (needs a reload)')
    p.note('Drag a window\'s gold corner grip to resize it; right-click the grip for normal size.')
    p.buttons(['!Reset Window Sizes...'])
    p.note('A window that wasn\'t restyled: point at it and type /skins this.')
    p.band('Minimap', 'AetherSkins')
    p.check('Minimap in the Aether look (needs a reload)')
    p.choice('Sun or moon', ['Follow the game', 'Day', 'Night'], 'Follow the game', new=True)
    p.check('AetherHub button on the minimap')
    p.gap(4)
    p.buttons(['!Restore Defaults...'])
L.render_b('Window Look', page, 'out_hub_look')
