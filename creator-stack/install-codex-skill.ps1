[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$Source = Join-Path $PSScriptRoot 'skills/creator-stack'
$Skills = Join-Path $HOME '.agents/skills'
$Target = Join-Path $Skills 'creator-stack'
$SourceManifest = Join-Path $Source 'SKILL.md'
$TargetManifest = Join-Path $Target 'SKILL.md'
if (-not (Test-Path -LiteralPath $SourceManifest -PathType Leaf)) { throw 'Bundled SKILL.md not found.' }
if (Test-Path -LiteralPath $Target) {
    if ((Test-Path -LiteralPath $TargetManifest -PathType Leaf) -and
        ((Get-FileHash -LiteralPath $SourceManifest -Algorithm SHA256).Hash -eq
         (Get-FileHash -LiteralPath $TargetManifest -Algorithm SHA256).Hash)) {
        Write-Output "Skill already installed: $TargetManifest"
        return
    }
    throw "A different creator-stack skill already exists; not overwriting $Target."
}
New-Item -Path $Skills -ItemType Directory -Force | Out-Null
Copy-Item -LiteralPath $Source -Destination $Target -Recurse
if ((Get-FileHash -LiteralPath $SourceManifest -Algorithm SHA256).Hash -ne
    (Get-FileHash -LiteralPath $TargetManifest -Algorithm SHA256).Hash) { throw 'Skill copy did not verify.' }
Write-Output "Skill installed: $TargetManifest"
