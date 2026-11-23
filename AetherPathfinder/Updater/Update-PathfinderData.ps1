<#
  AetherPathfinder updater for WoW Forever.

  Downloads the latest WoW Forever NPC data from QuestieDB
  (https://github.com/Questie/QuestieDB) into AetherPathfinder_Raw.lua. If anything
  goes wrong (no internet, GitHub down, unexpected file), it keeps the data you
  already have. It never starts or touches the game.

  Usage (AetherAddons-README.txt has the one-line setup command):
    Update-PathfinderData.ps1                    refresh once
    Update-PathfinderData.ps1 -InstallSchedule   refresh now, then automatically every day at
                                                 3:00 AM Mountain Time
    Update-PathfinderData.ps1 -RemoveSchedule    stop the automatic refresh
#>
param(
    [switch]$InstallSchedule,
    [switch]$RemoveSchedule,
    [switch]$NoLaunch      # no longer does anything; kept so older scheduled tasks keep working
)

$ErrorActionPreference = "Stop"
$addonDir = Split-Path -Parent $PSScriptRoot          # ...\AddOns\AetherPathfinder
$rawFile  = Join-Path $addonDir "AetherPathfinder_Raw.lua"
$logFile  = Join-Path $PSScriptRoot "update-log.txt"
$repo     = "Questie/QuestieDB"
$branch   = "master"
$npcPath  = "data/Forever/foreverNpcDB.lua"
$zonePath = "support/Forever/Zones/areaIdToUiMapId.lua"

function Log($msg) {
    $line = "{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Write-Host $line
    try { Add-Content -Path $logFile -Value $line -Encoding UTF8 } catch {}
}

# ---------- Automatic refresh (Windows Task Scheduler, current user, no admin) ----------
$taskName = "AetherPathfinder Refresh"

if ($RemoveSchedule) {
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "Automatic refresh turned off."
    } else {
        Write-Host "Automatic refresh wasn't set up."
    }
    exit 0
}

if ($InstallSchedule) {
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`"" `
        -WorkingDirectory $PSScriptRoot
    # Every day at 3:00 AM Mountain Time. Pinned to Arizona time (MST, UTC-7, no
    # daylight saving), so the run time doesn't move with clock or time-zone changes.
    $trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
    $trigger.StartBoundary = (Get-Date).ToString("yyyy-MM-dd") + "T03:00:00-07:00"
    # If the PC is off or asleep at 3:00 AM, run as soon as it's back on.
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings `
        -Description "Downloads the latest WoW Forever NPC data from QuestieDB for the AetherPathfinder addon, daily at 3:00 AM Mountain Time." `
        -Force | Out-Null
    $local = ([DateTimeOffset]::Parse("2000-01-01T03:00:00-07:00")).ToLocalTime().ToString("h:mm tt")
    Write-Host "Automatic refresh is on: every day at 3:00 AM Mountain Time ($local on this PC's clock)."
    Write-Host "If the PC is off or asleep then, it runs as soon as it's back on."
    Write-Host ""
    Write-Host "Running the first refresh now..."
    & $PSCommandPath
    exit 0
}

# ---------- Refresh ----------
function Get-Text($url) {
    # TLS 1.2 for older Windows PowerShell versions
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 20 `
        -Headers @{ "User-Agent" = "AetherPathfinder-Updater" }
    # Raw GitHub files are UTF-8; decode the bytes ourselves so names keep their accents.
    if ($resp.RawContentStream) {
        $resp.RawContentStream.Position = 0
        $bytes = $resp.RawContentStream.ToArray()
        return [Text.Encoding]::UTF8.GetString($bytes)
    }
    return $resp.Content
}

# A label for this data: the QuestieDB commit if GitHub's API answers, otherwise a
# fingerprint of the data itself (so the label only changes when the data does).
function Get-Version($text) {
    try {
        $api = "https://api.github.com/repos/$repo/commits?path=$npcPath&sha=$branch&per_page=1"
        $c = Invoke-RestMethod -Uri $api -TimeoutSec 10 -Headers @{ "User-Agent" = "AetherPathfinder-Updater" }
        if ($c -and $c[0]) {
            return "{0} ({1})" -f $c[0].sha.Substring(0, 7), ([datetime]$c[0].commit.committer.date).ToString("yyyy-MM-dd")
        }
    } catch {}
    $sha = [Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($text))
    return "data " + ([BitConverter]::ToString($hash).Replace("-", "").Substring(0, 8).ToLower())
}

function Update-Data() {
    $base = "https://raw.githubusercontent.com/$repo/$branch"
    Log "Downloading QuestieDB Forever data..."
    $npcText  = Get-Text "$base/$npcPath"
    $zoneText = Get-Text "$base/$zonePath"

    # The NPC table is the Lua code inside  QuestieDB.npcData = [[ ... ]]
    $m = [regex]::Match($npcText, 'QuestieDB\.npcData\s*=\s*\[\[(.*)\]\]', 'Singleline')
    if (-not $m.Success) { throw "NPC file format changed (npcData block not found)" }
    $npc = $m.Groups[1].Value.Trim()
    if (-not $npc.StartsWith("return {") -or $npc.Length -lt 500000) {
        throw "NPC data looks wrong ($($npc.Length) characters)"
    }

    # Zone tables are the  [[return { ... }]]  blocks in the zone file
    $zones = [regex]::Matches($zoneText, '=\s*\[\[(return \{.*?\})\]\]', 'Singleline') |
        ForEach-Object { $_.Groups[1].Value }
    if (@($zones).Count -lt 1) { throw "Zone file format changed (no tables found)" }

    foreach ($chunk in @($npc) + @($zones)) {
        if ($chunk.Contains("]====]")) { throw "Unexpected text in the data" }
    }

    $version = Get-Version ($npc + ($zones -join ""))
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("-- Written by Updater\Update-PathfinderData.ps1. Do not edit; it is replaced on each refresh.")
    [void]$sb.AppendLine("-- Source: https://github.com/$repo ($npcPath, $zonePath)")
    [void]$sb.AppendLine("AetherPathfinder_RawSource = {")
    [void]$sb.AppendLine("version = `"$version`",")
    [void]$sb.AppendLine("npc = [====[")
    [void]$sb.AppendLine($npc)
    [void]$sb.AppendLine("]====],")
    [void]$sb.AppendLine("areas = {")
    foreach ($z in $zones) {
        [void]$sb.AppendLine("[====[")
        [void]$sb.AppendLine($z)
        [void]$sb.AppendLine("]====],")
    }
    [void]$sb.AppendLine("},")
    [void]$sb.AppendLine("}")
    $newText = $sb.ToString()

    if ((Test-Path $rawFile) -and ((Get-Content $rawFile -Raw -Encoding UTF8) -eq $newText)) {
        Log "Already up to date ($version)."
        return
    }
    # Write to a temp file first so a failed write never leaves a broken file behind.
    $tmp = "$rawFile.tmp"
    [IO.File]::WriteAllText($tmp, $newText, (New-Object Text.UTF8Encoding $false))
    Move-Item -Path $tmp -Destination $rawFile -Force
    Log "Updated AetherPathfinder data to QuestieDB $version."
}

try {
    Update-Data
} catch {
    Log "Refresh skipped: $($_.Exception.Message). Keeping the current data."
}
