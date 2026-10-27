param(
    [ValidateRange(1, 65535)][int]$Port = 8765,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$uiPath = Join-Path $projectRoot 'web\dist\index.html'
$databasePath = Join-Path $projectRoot 'data\reference.sqlite3'
$url = "http://127.0.0.1:$Port"
if (!(Test-Path -LiteralPath $pythonPath)) { throw 'Run uv sync --extra web first.' }
if (!(Test-Path -LiteralPath $uiPath)) { throw 'Build the interface first: cd web; npm ci; npm run build.' }
if (!(Test-Path -LiteralPath $databasePath)) { throw 'Import the reviewed source selections first; see README.md.' }

$ready = $false
try {
    $existing = Invoke-RestMethod "$url/api/meta" -TimeoutSec 2
    if ($existing.app -ne 'prompt-reference') { throw "Port $Port is used by another service." }
    $ready = $true
} catch {
    if ($_.Exception.Message -like '*used by another service*') { throw }
}

if (!$ready) {
    $logDir = Join-Path $projectRoot 'data\logs'
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $process = Start-Process -FilePath $pythonPath -WorkingDirectory $projectRoot `
        -ArgumentList @('-m', 'prompt_reference.cli', 'serve', '--port', "$Port") `
        -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $logDir "workbench-$Port.stdout.log") `
        -RedirectStandardError (Join-Path $logDir "workbench-$Port.stderr.log")
    Set-Content -LiteralPath (Join-Path $logDir "workbench-$Port.pid") -Value $process.Id
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Milliseconds 200
        try {
            $meta = Invoke-RestMethod "$url/api/meta" -TimeoutSec 1
            if ($meta.app -eq 'prompt-reference') { $ready = $true; break }
        } catch { }
        if ($process.HasExited) { break }
    }
}
if (!$ready) { throw "Workbench did not start. Check data\logs\workbench-$Port.stderr.log." }
Write-Output "Cowabunga AI is running at $url"
if (!$NoBrowser) { Start-Process $url }
