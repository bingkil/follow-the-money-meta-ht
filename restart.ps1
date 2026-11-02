# Run from any directory: & C:\path\to\follow-the-money-meta-ht\restart.ps1
[CmdletBinding()]
param(
    [switch]$OpenBrowser,
    [ValidateRange(5, 300)][int]$TimeoutSeconds = 60
)

$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') {
    throw 'restart.ps1 requires Windows.'
}
$projectRoot = $PSScriptRoot
$launcher = Join-Path $projectRoot 'scripts\dev-server.ps1'
foreach ($command in @('uv', 'npm.cmd')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "$command is required. Install it and open a new terminal first."
    }
}

# Match this checkout's absolute path as well as a known server signature.
# Never kill every python.exe/node.exe process or an arbitrary port owner.
$servers = @(Get-CimInstance Win32_Process | Where-Object {
    $text = [string]$_.CommandLine
    $executable = [string]$_.ExecutablePath
    $belongsHere = $text.IndexOf($projectRoot, [StringComparison]::OrdinalIgnoreCase) -ge 0 -or
        $executable.StartsWith($projectRoot + '\', [StringComparison]::OrdinalIgnoreCase)
    $knownServer = $text -match 'dev-server\.ps1|uvicorn.+ftm\.api:app|[\\/]vite[\\/].*vite\.js'
    $belongsHere -and $knownServer -and $_.ProcessId -ne $PID
})
foreach ($server in $servers) {
    # Another matched parent's process tree may already have removed this process.
    $current = Get-CimInstance Win32_Process -Filter "ProcessId = $($server.ProcessId)"
    if ($current -and $current.CreationDate -eq $server.CreationDate) {
        Write-Host "Stopping FTM process tree $($server.ProcessId)..."
        & taskkill.exe /PID $server.ProcessId /T /F 2>&1 | Out-Host
        if ($LASTEXITCODE -ne 0 -and (Get-Process -Id $server.ProcessId -ErrorAction SilentlyContinue)) {
            throw "Could not stop FTM process $($server.ProcessId)."
        }
    }
}

# Ask the OS whether a port can be bound. Leave unrelated listeners running.
function Find-FreePort([int]$StartPort, [int]$ExcludedPort = 0) {
    for ($candidate = $StartPort; $candidate -le 65535; $candidate++) {
        if ($candidate -eq $ExcludedPort) { continue }
        $listener = [System.Net.Sockets.TcpListener]::new(
            [System.Net.IPAddress]::Loopback, $candidate)
        try {
            $listener.Server.ExclusiveAddressUse = $true
            $listener.Start()
            return $candidate
        } catch [System.Net.Sockets.SocketException] {
            # Occupied or reserved: try the next port.
        } finally {
            $listener.Stop()
        }
    }
    throw "No available TCP port found starting at $StartPort."
}
$backendPort = Find-FreePort 8000
$frontendPort = Find-FreePort 5173 $backendPort
$backendUrl = "http://127.0.0.1:$backendPort"
$frontendUrl = "http://127.0.0.1:$frontendPort"
Write-Host "Selected backend port $backendPort and frontend port $frontendPort."

$shell = (Get-Process -Id $PID).Path
# Server windows use -NoProfile, so hand them the directories of the tools found here.
$toolDirs = foreach ($command in @('uv', 'npm.cmd')) { Split-Path (Get-Command $command).Source }
$env:PATH = (($toolDirs | Select-Object -Unique) + $env:PATH) -join ';'
foreach ($service in @('backend', 'frontend')) {
    # Arguments are passed to PowerShell's -File parser. Windows paths cannot contain quotes.
    $arguments = @('-NoProfile', '-NoExit', '-ExecutionPolicy', 'Bypass', '-File',
        ('"{0}"' -f $launcher), '-ProjectRoot', ('"{0}"' -f $projectRoot),
        '-Service', $service, '-Port',
        $(if ($service -eq 'backend') { $backendPort } else { $frontendPort }),
        '-ApiPort', $backendPort)
    Start-Process -FilePath $shell -ArgumentList $arguments -WorkingDirectory $projectRoot |
        Out-Null
}

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$ready = $false
do {
    try {
        $health = Invoke-RestMethod "$backendUrl/api/health" -TimeoutSec 2
        $page = Invoke-WebRequest $frontendUrl -UseBasicParsing -TimeoutSec 2
        $proxyHealth = Invoke-RestMethod "$frontendUrl/api/health" -TimeoutSec 2
        $ready = $health.status -eq 'ok' -and $proxyHealth.status -eq 'ok' -and
            $page.StatusCode -eq 200
    } catch {
        $ready = $false
    }
    if (-not $ready) { Start-Sleep -Milliseconds 500 }
} while (-not $ready -and (Get-Date) -lt $deadline)
if (-not $ready) {
    throw "Servers did not become ready within $TimeoutSeconds seconds. Check the two server windows; dependency installation may need more time."
}
Write-Host "FTM ready: $frontendUrl" -ForegroundColor Green
Write-Host "API documentation: $backendUrl/docs"
if ($OpenBrowser) { Start-Process $frontendUrl }
