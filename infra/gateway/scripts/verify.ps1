$ErrorActionPreference = "Stop"

Push-Location .\infra\gateway

try {
    if (-not (Test-Path .\.venv)) {
        py -m venv .venv
    }

    .\.venv\Scripts\Activate.ps1
    pip install -r requirements-dev.txt

    pytest -q
}
finally {
    Pop-Location
}

docker build -t smart-education-gateway .\infra\gateway

Write-Host "Static gateway verification complete."
Write-Host "For Docker route integration run:"
Write-Host ".\infra\gateway\scripts\integration-smoke.ps1"
