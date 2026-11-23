-- ==========================================
-- AetherPathfinder: build the NPC list from freshly downloaded QuestieDB data.
-- The updater (Updater\Update-PathfinderData.ps1) saves QuestieDB's files into
-- AetherPathfinder_Raw.lua before WoW starts. If that data is there and looks
-- right, it replaces the built-in list in AetherPathfinder_Data.lua for this session.
-- ==========================================

local raw = AetherPathfinder_RawSource
AetherPathfinder_RawSource = nil          -- the raw text is large; let it be freed
AetherPathfinder_SeedInfo = { source = "built-in" }

if type(raw) ~= "table" or type(raw.npc) ~= "string" or type(raw.areas) ~= "table" then
    return
end

local compile = loadstring or load

local function Run(chunk)
    local fn = compile(chunk)
    if not fn then return nil end
    local ok, result = pcall(fn)
    if ok and type(result) == "table" then return result end
    return nil
end

local VENDOR, FLIGHT, TRAINER, INN, BANK, AUCTION, STABLE, REPAIR =
    4, 8, 16, 128, 256, 4096, 8192, 16384
local SERVICE_FLAGS = { VENDOR, FLIGHT, TRAINER, INN, BANK, AUCTION, STABLE, REPAIR }
local FACTION_CODE = { A = 1, H = 2, AH = 3 }

local function HasFlag(flags, bit)
    return flags % (bit * 2) >= bit
end

local function IsService(flags)
    for _, bit in ipairs(SERVICE_FLAGS) do
        if HasFlag(flags, bit) then return true end
    end
    return false
end

local function Build()
    local npcs = Run(raw.npc)
    if not npcs then return nil, "couldn't read the NPC data" end

    -- Area -> world map ID. The file lists its overrides first and its main table
    -- last, so apply them from last to first and let the overrides win.
    local areaToMap = {}
    for i = #raw.areas, 1, -1 do
        local t = Run(raw.areas[i])
        if t then
            for area, mapID in pairs(t) do areaToMap[area] = mapID end
        end
    end
    if not next(areaToMap) then return nil, "couldn't read the zone data" end

    local seed, count = {}, 0
    for id, d in pairs(npcs) do
        local name, spawns, faction, sub, flags = d[1], d[7], d[13], d[14], d[15] or 0
        local fac = faction and FACTION_CODE[faction]
        local seasonal = type(sub) == "string" and sub:lower():find("smokywood", 1, true)
        if fac and type(spawns) == "table" and IsService(flags) and not seasonal then
            for area, coords in pairs(spawns) do
                local mapID = areaToMap[area]
                if mapID and mapID > 0 and type(coords) == "table" then
                    for _, c in ipairs(coords) do
                        local x, y = c[1], c[2]
                        if x and y and x >= 0 and y >= 0 then
                            seed[mapID] = seed[mapID] or {}
                            table.insert(seed[mapID], {
                                id, name, sub or "", flags, fac,
                                math.floor(x * 100 + 0.5) / 10000,
                                math.floor(y * 100 + 0.5) / 10000,
                            })
                            count = count + 1
                        end
                    end
                end
            end
        end
    end
    return seed, count
end

local ok, seed, count = pcall(Build)
-- Sanity check: a good download has well over a thousand service NPCs.
if ok and seed and type(count) == "number" and count >= 500 then
    AetherPathfinder_Seed = seed
    AetherPathfinder_SeedInfo = { source = "downloaded", version = raw.version, count = count }
else
    AetherPathfinder_SeedInfo = { source = "built-in",
        problem = ok and tostring(count or "too few NPCs") or tostring(seed) }
end
collectgarbage()
