$ErrorActionPreference = 'Stop'
if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64') { throw 'This pinned setup targets native Windows x64.' }
$version = 'v1.2.1'
$archive = 'rtk-oss-x86_64-pc-windows-msvc.zip'
$sha = '43124168ec0733b50f7e9e1f1b994ced9b0693b9e92281428f64990c308bf1c8'
$upstream = Join-Path (Split-Path -Parent $PSScriptRoot) 'upstream\token'
$bin = Join-Path $PSScriptRoot 'bin'
New-Item -ItemType Directory -Path $upstream,$bin -Force | Out-Null
$dest = Join-Path $upstream $archive
if (-not (Test-Path -LiteralPath $dest)) {
    $partial = Join-Path $upstream ("temporary-" + [guid]::NewGuid() + ".zip")
    try {
        Invoke-WebRequest -Uri "https://github.com/rtk-ai/rtk/releases/download/$version/$archive" -OutFile $partial
        if ((Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash.ToLowerInvariant() -ne $sha) { throw 'RTK release SHA-256 mismatch.' }
        Move-Item -LiteralPath $partial -Destination $dest
    } finally {
        if (Test-Path -LiteralPath $partial) { Remove-Item -LiteralPath $partial }
    }
}
if ((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $sha) { throw 'Existing RTK release SHA-256 mismatch.' }
Expand-Archive -LiteralPath $dest -DestinationPath $bin -Force
& (Join-Path $bin 'rtk.exe') --version
if ($LASTEXITCODE -ne 0) { throw 'RTK did not start.' }
