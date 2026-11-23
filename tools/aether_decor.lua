-- Aether window trim: a double blue frame with a soft halo, gold corner
-- brackets, a title strip with a gold underline, and a small gold gem at the
-- top center. Plain colored textures only. titleHeight 0 = no title strip.
local function AetherDecorate(frame, titleHeight)
    if frame.aetherTrim then return end
    frame.aetherTrim = true
    local function Rect(layer, sub, r, g, b, a)
        local t = frame:CreateTexture(nil, layer, nil, sub)
        t:SetColorTexture(r, g, b, a)
        return t
    end
    -- Soft halo just outside the border.
    local HALO = 4
    for _, side in ipairs({ "TOP", "BOTTOM", "LEFT", "RIGHT" }) do
        local t = Rect("BACKGROUND", -8, 0.3, 0.65, 1, 0.12)
        if side == "TOP" then
            t:SetPoint("BOTTOMLEFT", frame, "TOPLEFT", -HALO, 0); t:SetPoint("BOTTOMRIGHT", frame, "TOPRIGHT", HALO, 0); t:SetHeight(HALO)
        elseif side == "BOTTOM" then
            t:SetPoint("TOPLEFT", frame, "BOTTOMLEFT", -HALO, 0); t:SetPoint("TOPRIGHT", frame, "BOTTOMRIGHT", HALO, 0); t:SetHeight(HALO)
        elseif side == "LEFT" then
            t:SetPoint("TOPRIGHT", frame, "TOPLEFT", 0, 0); t:SetPoint("BOTTOMRIGHT", frame, "BOTTOMLEFT", 0, 0); t:SetWidth(HALO)
        else
            t:SetPoint("TOPLEFT", frame, "TOPRIGHT", 0, 0); t:SetPoint("BOTTOMLEFT", frame, "BOTTOMRIGHT", 0, 0); t:SetWidth(HALO)
        end
    end
    -- Inner frame line, 3 pixels in.
    local IN = 3
    for _, side in ipairs({ "TOP", "BOTTOM", "LEFT", "RIGHT" }) do
        local t = Rect("BORDER", 1, 0.3, 0.65, 1, 0.3)
        if side == "TOP" or side == "BOTTOM" then
            t:SetPoint(side .. "LEFT", frame, side .. "LEFT", IN, side == "TOP" and -IN or IN)
            t:SetPoint(side .. "RIGHT", frame, side .. "RIGHT", -IN, side == "TOP" and -IN or IN)
            t:SetHeight(1)
        else
            t:SetPoint("TOP" .. side, frame, "TOP" .. side, side == "LEFT" and IN or -IN, -IN)
            t:SetPoint("BOTTOM" .. side, frame, "BOTTOM" .. side, side == "LEFT" and IN or -IN, IN)
            t:SetWidth(1)
        end
    end
    -- Title strip with a gold underline.
    if titleHeight and titleHeight > 0 then
        local strip = Rect("BORDER", 0, 0.075, 0.157, 0.29, 1)
        strip:SetPoint("TOPLEFT", frame, "TOPLEFT", IN + 1, -(IN + 1))
        strip:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -(IN + 1), -(IN + 1))
        strip:SetHeight(titleHeight - IN - 1)
        local line = Rect("BORDER", 2, 1, 0.82, 0, 0.7)
        line:SetPoint("TOPLEFT", strip, "BOTTOMLEFT", 0, 0)
        line:SetPoint("TOPRIGHT", strip, "BOTTOMRIGHT", 0, 0)
        line:SetHeight(1)
    end
    -- Gold corner brackets, just outside each corner.
    local LEN, W, OUT = 12, 2, 3
    for _, corner in ipairs({ "TOPLEFT", "TOPRIGHT", "BOTTOMLEFT", "BOTTOMRIGHT" }) do
        local dx = corner:find("LEFT") and -OUT or OUT
        local dy = corner:find("TOP") and OUT or -OUT
        local across = Rect("OVERLAY", 6, 1, 0.82, 0, 1)
        across:SetSize(LEN, W)
        across:SetPoint(corner, frame, corner, dx, dy)
        local down = Rect("OVERLAY", 6, 1, 0.82, 0, 1)
        down:SetSize(W, LEN)
        down:SetPoint(corner, frame, corner, dx, dy)
    end
    -- Gem at the top center: a gold diamond with a dark rim.
    local rim = Rect("OVERLAY", 6, 0.04, 0.05, 0.07, 1)
    rim:SetSize(11, 11)
    rim:SetPoint("CENTER", frame, "TOP", 0, 0)
    local gem = Rect("OVERLAY", 7, 1, 0.82, 0, 1)
    gem:SetSize(8, 8)
    gem:SetPoint("CENTER", frame, "TOP", 0, 0)
    if gem.SetRotation then
        rim:SetRotation(math.pi / 4)
        gem:SetRotation(math.pi / 4)
    end
end

