-- ==========================================
-- AetherLedger: where the default tooltip goes
-- Tooltips the game puts in its default spot (bottom right, over the
-- meter) go just left of the quest tracker instead, centered at
-- mid-screen. If you move the tracker in Edit Mode, they follow it; if the
-- tracker sits too close to the left edge, they go on its right.
-- Tooltips that something places on purpose (by your mouse, beside a
-- button or a bag) are left alone: only the default spot is changed.
-- /ledger tooltip turns it on or off.
-- ==========================================

local GAP = 8        -- UI units between the tooltip and the tracker
local MIN_ROOM = 240 -- room needed on the tracker's left (a wide tooltip)

local function Enabled()
    return not (AetherLedgerDB and AetherLedgerDB.tooltipSpot == false)
end

-- The tracker's left and right edges in UIParent units, or nil.
local function TrackerEdges()
    local t = _G.ObjectiveTrackerFrame
    if not (t and t.GetLeft and UIParent) then return end
    local left, right = t:GetLeft(), t:GetRight()
    if not (left and right) then return end
    local k = t:GetEffectiveScale() / UIParent:GetEffectiveScale()
    return left * k, right * k
end

local function Place(tooltip)
    if not Enabled() or not tooltip or tooltip:IsForbidden() then return end
    local left, right = TrackerEdges()
    if not left then return end            -- no tracker: keep the game's spot
    tooltip:ClearAllPoints()
    if left >= MIN_ROOM then
        tooltip:SetPoint("RIGHT", UIParent, "LEFT", left - GAP, 0)
    else
        tooltip:SetPoint("LEFT", UIParent, "LEFT", right + GAP, 0)
    end
end

if GameTooltip_SetDefaultAnchor then
    hooksecurefunc("GameTooltip_SetDefaultAnchor", function(tooltip)
        pcall(Place, tooltip)
    end)
end

AetherLedger_TooltipSpot = {
    Place = Place,
    Toggle = function()
        AetherLedgerDB = AetherLedgerDB or {}
        AetherLedgerDB.tooltipSpot = not Enabled()
        return Enabled()
    end,
    Enabled = Enabled,
}
