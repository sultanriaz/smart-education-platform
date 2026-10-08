param(
    [string]$RepoRoot = (Get-Location).Path,
    [int]$Workers = 4
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if (-not (Test-Path ".env.performance")) {
    throw "Copy .env.performance.example to .env.performance and configure QA credentials."
}

New-Item -ItemType Directory -Force `
    -Path ".\tests\performance\results\distributed" | Out-Null

docker compose `
    -f .\docker-compose.performance.yml `
    --env-file .\.env.performance `
    up `
    --abort-on-container-exit `
    --scale "locust-worker=$Workers"

$Stats = ".\tests\performance\results\distributed\locust_stats.csv"
if (Test-Path $Stats) {
    python .\scripts\evaluate-performance.py `
        $Stats `
        --output ".\tests\performance\results\distributed\evaluation.json"
}
