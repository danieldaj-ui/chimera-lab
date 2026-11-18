# Installs Chimera Lab.vst3 (kept beside this script) into the system VST3 folder,
# backing up any existing copy first. Needs administrator rights; it asks for them.
$ErrorActionPreference = 'Stop'

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -Verb RunAs -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"")
    exit
}

try {
    $source = Join-Path $PSScriptRoot 'Chimera Lab.vst3'
    $dll = Join-Path $source 'Contents\x86_64-win\Chimera Lab.vst3'
    if (-not (Test-Path -LiteralPath $dll -PathType Leaf)) {
        throw 'Keep this installer beside the Chimera Lab.vst3 folder.'
    }

    $common = [Environment]::GetFolderPath('CommonProgramFiles')   # C:\Program Files\Common Files
    $folder = Join-Path $common 'VST3'
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
    $destination = Join-Path $folder 'Chimera Lab.vst3'

    $stage = Join-Path $folder ('.chimera-update-' + [guid]::NewGuid().ToString('N'))
    Copy-Item -LiteralPath $source -Destination $stage -Recurse

    $backup = $null
    if (Test-Path -LiteralPath $destination) {
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-ffffff'
        $backupDir = Join-Path (Join-Path $common 'Chimera Lab Backups') $stamp
        New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
        $backup = Join-Path $backupDir 'Chimera Lab.vst3'
        Move-Item -LiteralPath $destination -Destination $backup
    }
    try {
        Move-Item -LiteralPath $stage -Destination $destination
    } catch {
        if ($backup) { Move-Item -LiteralPath $backup -Destination $destination }
        throw
    }

    Write-Host "Installed Chimera Lab 0.4 to $destination"
    Write-Host 'Restart your DAW; rescan VST3 plug-ins if it does not appear.'
    if ($backup) { Write-Host "Previous build preserved at: $backup" }
} catch {
    Write-Host "Install failed: $_" -ForegroundColor Red
}
Read-Host 'Press Enter to close'
