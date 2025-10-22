#requires -Version 5.1
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$psExe = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
$launcher = Join-Path $root 'START_HTTP_SERVER.ps1'
$desktop = [Environment]::GetFolderPath('Desktop')

function New-OrfeasShortcut {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$Mode
    )
    $lnkPath = Join-Path $desktop "$Name.lnk"
    $ws = New-Object -ComObject WScript.Shell
    $sc = $ws.CreateShortcut($lnkPath)
    $sc.TargetPath = $psExe
    $sc.Arguments  = "-NoLogo -NoExit -ExecutionPolicy Bypass -File `"$launcher`" -Mode $Mode"
    $sc.WorkingDirectory = $root
    $sc.WindowStyle = 1
    $sc.IconLocation = "$psExe,0"
    $sc.Save()
    Write-Host "[OK] Created: $lnkPath" -ForegroundColor Green
}

if (-not (Test-Path $launcher)) {
    throw "Launcher script not found: $launcher"
}

New-OrfeasShortcut -Name 'ORFEAS Studio (Powerful 3D)' -Mode 'powerful_3d'
New-OrfeasShortcut -Name 'ORFEAS Studio (Full AI)'     -Mode 'full_ai'

Write-Host "Shortcuts created on Desktop. Double-click to launch in selected mode." -ForegroundColor Cyan
