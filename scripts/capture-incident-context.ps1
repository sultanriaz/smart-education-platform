param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if (-not $OutputRoot) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $OutputRoot = Join-Path $RepoRoot "incident-artifacts\$Stamp"
}
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

# Operational metadata only. Do not dump environment variables because they may
# contain secrets.
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" |
    Set-Content -Encoding utf8 (Join-Path $OutputRoot "docker-ps.txt")

try {
    Invoke-WebRequest `
        -UseBasicParsing `
        http://localhost:9090/api/v1/alerts `
        -OutFile (Join-Path $OutputRoot "prometheus-alerts.json")
}
catch {
    $_ | Out-String | Set-Content -Encoding utf8 `
        (Join-Path $OutputRoot "prometheus-alerts-error.txt")
}

try {
    Invoke-WebRequest `
        -UseBasicParsing `
        http://localhost:9090/api/v1/targets `
        -OutFile (Join-Path $OutputRoot "prometheus-targets.json")
}
catch {
    $_ | Out-String | Set-Content -Encoding utf8 `
        (Join-Path $OutputRoot "prometheus-targets-error.txt")
}

Write-Host "Incident context written to: $OutputRoot"
Write-Host "Review artifacts before sharing; do not attach secrets/tokens."
