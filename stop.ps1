# Stop this checkout's FTM development servers without restarting them.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') {
    throw 'stop.ps1 requires Windows.'
}
$projectRoot = $PSScriptRoot

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
        $kill = Start-Process -FilePath 'taskkill.exe' -ArgumentList @(
            '/PID', [string]$server.ProcessId, '/T', '/F'
        ) -NoNewWindow -Wait -PassThru
        if ($kill.ExitCode -ne 0 -and (Get-Process -Id $server.ProcessId -ErrorAction SilentlyContinue)) {
            throw "Could not stop FTM process $($server.ProcessId)."
        }
    }
}

if ($servers.Count -eq 0) {
    Write-Host 'No FTM servers found for this checkout.'
} else {
    Write-Host 'FTM servers stopped.' -ForegroundColor Green
}
