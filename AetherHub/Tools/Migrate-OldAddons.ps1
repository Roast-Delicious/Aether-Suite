<#
  One-time move from the old addon names to the Aether names:
    CleanBars -> AetherBars, MapCoords -> AetherCoords,
    PathfinderMap -> AetherPathfinder, QuarryMarks -> AetherMarks

  1. Copies each old addon's saved settings into the new addon's settings file
     (for your account and every character), so nothing is lost. This includes
     the NPCs PathfinderMap learned.
  2. Moves the old addon folders out of AddOns, into Interface\AddOns_old_backup,
     so the old and new versions don't both load.
  3. Removes the old "WoW Forever (PathfinderMap refresh)" desktop shortcut.
     For the automatic refresh, run the setup command instead
     (see AetherAddons-README.txt).

  Close WoW before running this: WoW rewrites settings files when it exits.
  Running it a second time is safe; it only acts on what's still left to move.
#>
$ErrorActionPreference = "Stop"

$hubDir    = Split-Path -Parent $PSScriptRoot      # ...\AddOns\AetherHub
$addonsDir = Split-Path -Parent $hubDir            # ...\Interface\AddOns
$interface = Split-Path -Parent $addonsDir         # ...\Interface
$gameDir   = Split-Path -Parent $interface         # ...\_forever_
$wtfDir    = Join-Path $gameDir "WTF\Account"
$backupDir = Join-Path $interface "AddOns_old_backup"

$renames = [ordered]@{
    "CleanBars"     = "AetherBars"
    "MapCoords"     = "AetherCoords"
    "PathfinderMap" = "AetherPathfinder"
    "QuarryMarks"   = "AetherMarks"
}

function Say($msg) { Write-Host $msg }

if (Get-Process -Name "WowClassic", "Wow", "WowForever" -ErrorAction SilentlyContinue) {
    Say "WoW is running. Close the game completely, then run this again."
    exit 1
}

# ---------- 1. Settings files ----------
$moved = 0
if (Test-Path $wtfDir) {
    foreach ($old in $renames.Keys) {
        $new = $renames[$old]
        $files = Get-ChildItem -Path $wtfDir -Recurse -File -Filter "$old.lua" |
            Where-Object { $_.Directory.Name -eq "SavedVariables" }
        foreach ($f in $files) {
            $target = Join-Path $f.DirectoryName "$new.lua"
            $oldText = [IO.File]::ReadAllText($f.FullName)
            # The new addon reads the old names too, so the old file's contents can be
            # added to the new file as they are. It switches to the new names on load.
            if (Test-Path $target) {
                [IO.File]::AppendAllText($target, "`r`n" + $oldText)
            } else {
                [IO.File]::WriteAllText($target, $oldText)
            }
            Rename-Item -Path $f.FullName -NewName "$old.lua.migrated" -Force
            $where = $f.DirectoryName.Substring($wtfDir.Length).TrimStart("\")
            Say "Settings: $old -> $new  ($where)"
            $moved++
        }
    }
} else {
    Say "No WTF folder found at $wtfDir (nothing to copy)."
}
if ($moved -eq 0) { Say "Settings: nothing left to move." }

# ---------- 2. Old addon folders ----------
foreach ($old in $renames.Keys) {
    $oldDir = Join-Path $addonsDir $old
    if (Test-Path $oldDir) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        $dest = Join-Path $backupDir $old
        if (Test-Path $dest) { $dest = "$dest-" + (Get-Date -Format "yyyyMMddHHmmss") }
        Move-Item -Path $oldDir -Destination $dest
        Say "Folder: moved AddOns\$old to AddOns_old_backup"
    }
}

# ---------- 3. Desktop shortcut ----------
$desktop = [Environment]::GetFolderPath("Desktop")
$oldLnk = if ($desktop) { Join-Path $desktop "WoW Forever (PathfinderMap refresh).lnk" } else { $null }
if ($oldLnk -and (Test-Path $oldLnk)) {
    Remove-Item $oldLnk -Force
    Say "Shortcut: removed the old PathfinderMap shortcut. For the automatic refresh,"
    Say "          run the setup command from AetherAddons-README.txt."
}

Say ""
Say "Done. Start WoW; your settings will be waiting under the new names."
