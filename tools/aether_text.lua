-- ==========================================
-- AETHER TEXT
-- ==========================================
-- The Aether text style, in Fira Sans (the unit frames' font; SIL Open Font
-- License, see AetherHub\Media\Fonts\FiraSans-OFL.txt). In windows: Regular
-- for text, SemiBold for the gold headings, with a soft shadow. Over the game
-- world (AetherFontWorld...): Bold with a thin black outline and a shadow, so
-- it reads on any background, faded or not. Each copies the Blizzard font it
-- stands in for (size, color), so layouts stay the same. The files live in
-- AetherHub\Media\Fonts; if one can't load, Blizzard's font stays.
AETHER_FONT_DIR = AETHER_FONT_DIR or "Interface\\AddOns\\AetherHub\\Media\\Fonts\\FiraSans-"
local function AetherFontFile(weight) return AETHER_FONT_DIR .. weight .. ".ttf" end

-- Sets a Fira font on a font object or font string; false if it didn't load.
local function AetherSetFont(obj, weight, size, outline)
    local ok, set = pcall(obj.SetFont, obj, AetherFontFile(weight), size, outline and "OUTLINE" or "")
    return ok and set ~= false
end

if CreateFont and not AetherFontHighlight then
    -- Fira's capitals are a little shorter than Friz Quadrata's at the same size.
    local SCALE = 1.05
    local function Make(name, base, weight, world)
        local f = CreateFont(name)
        local src = _G[base]
        if src then f:CopyFontObject(src) end
        local file, size, flags = f:GetFont()
        size = size or 12
        if not AetherSetFont(f, weight, size * SCALE, world) and file then
            f:SetFont(file, size, flags or "")
        end
        f:SetShadowColor(0, 0, 0, world and 1 or 0.8)
        f:SetShadowOffset(1, -1)
    end
    for _, d in ipairs({
        { "AetherFontNormal",           "GameFontNormal",         "SemiBold" },
        { "AetherFontNormalSmall",      "GameFontNormalSmall",    "SemiBold" },
        { "AetherFontNormalLarge",      "GameFontNormalLarge",    "SemiBold" },
        { "AetherFontNormalHuge",       "GameFontNormalHuge",     "SemiBold" },
        { "AetherFontHighlight",        "GameFontHighlight",      "Regular" },
        { "AetherFontHighlightSmall",   "GameFontHighlightSmall", "Regular" },
        { "AetherFontDisable",          "GameFontDisable",        "Regular" },
        { "AetherFontDisableSmall",     "GameFontDisableSmall",   "Regular" },
        { "AetherFontWorldNormal",      "GameFontNormal",         "Bold", true },
        { "AetherFontWorldNormalSmall", "GameFontNormalSmall",    "Bold", true },
        { "AetherFontWorld",            "GameFontHighlight",      "Bold", true },
        { "AetherFontWorldSmall",       "GameFontHighlightSmall", "Bold", true },
    }) do Make(d[1], d[2], d[3], d[4]) end
end
