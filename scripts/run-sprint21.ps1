param(
    [string]$RepoRoot = (Get-Location).Path,
    [switch]$Live
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "=== smartedu-observability package ==="
Push-Location .\libs\python\smartedu_observability
try {
    python -m pytest -q
}
finally {
    Pop-Location
}

Write-Host "`n=== Observability config tests ==="
python -m pytest -q .\tests\observability

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "`n=== Prometheus config ==="
    docker run --rm `
        -v "${RepoRoot}\infra\observability\prometheus:/etc/prometheus:ro" `
        prom/prometheus:v2.55.1 `
        promtool check config /etc/prometheus/prometheus.yml

    Write-Host "`n=== Prometheus rules ==="
    docker run --rm `
        -v "${RepoRoot}\infra\observability\prometheus:/etc/prometheus:ro" `
        prom/prometheus:v2.55.1 `
        promtool check rules `
        /etc/prometheus/rules/recording.yml `
        /etc/prometheus/rules/alerts.yml
}
else {
    Write-Warning "Docker not found; promtool validation skipped."
}

if ($Live) {
    Write-Host "`n=== Live observability smoke ==="
    .\scripts\observability-smoke.ps1 -RequireServices
}
