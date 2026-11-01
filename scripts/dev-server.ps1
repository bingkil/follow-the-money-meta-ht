# Internal launcher used by restart.ps1; absolute paths identify this checkout's servers.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory)][ValidateSet('backend', 'frontend')][string]$Service,
    [Parameter(Mandatory)][ValidateRange(1,65535)][int]$Port,
    [Parameter(Mandatory)][ValidateRange(1,65535)][int]$ApiPort
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $ProjectRoot
$Host.UI.RawUI.WindowTitle = "FTM - $Service"
if ($Service -eq 'backend') {
    & uv sync --locked
    if ($LASTEXITCODE -ne 0) { throw 'uv sync failed.' }
    $env:PYTHONPATH = Join-Path $ProjectRoot 'services\api'
    $uvArguments = @('run')
    $envFile = Join-Path $ProjectRoot '.env'
    if (Test-Path -LiteralPath $envFile) { $uvArguments += @('--env-file', $envFile) }
    $uvArguments += @('uvicorn', 'ftm.api:app', '--app-dir', $env:PYTHONPATH,
        '--host', '127.0.0.1', '--port', [string]$Port, '--reload')
    & uv @uvArguments
    if ($LASTEXITCODE -ne 0) { throw 'Backend stopped with an error.' }
} else {
    Set-Location -LiteralPath (Join-Path $ProjectRoot 'apps\web')
    # npm ci also handles dependency/lockfile changes between restarts.
    & npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw 'npm ci failed.' }
    $env:FTM_API_TARGET = "http://127.0.0.1:$ApiPort"
    & npm.cmd run dev -- --host 127.0.0.1 --port $Port --strictPort
    if ($LASTEXITCODE -ne 0) { throw 'Frontend stopped with an error.' }
}
