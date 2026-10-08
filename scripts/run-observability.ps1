param(
    [string]$RepoRoot = (Get-Location).Path,
    [switch]$Logs,
    [switch]$Exporters,
    [switch]$HostMetrics
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if (-not (Test-Path ".env.observability")) {
    throw "Copy .env.observability.example to .env.observability and set GRAFANA_ADMIN_PASSWORD."
}

$Args = @(
    "compose",
    "-f", ".\docker-compose.observability.yml"
)

if ($Exporters) {
    $Args += @("-f", ".\docker-compose.observability.exporters.yml")
}

$Args += @("--env-file", ".\.env.observability")

if ($Logs) {
    $Args += @("--profile", "logs")
}
if ($HostMetrics) {
    $Args += @("--profile", "host-metrics")
}

$Args += @("up", "-d")

docker @Args

Write-Host ""
Write-Host "Grafana:      http://localhost:3001"
Write-Host "Prometheus:   http://localhost:9090"
Write-Host "Alertmanager: http://localhost:9093"
Write-Host "Tempo:        http://localhost:3200"
Write-Host "Loki:         http://localhost:3100"
