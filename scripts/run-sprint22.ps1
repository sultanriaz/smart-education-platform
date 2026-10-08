param([string]$RepoRoot=(Get-Location).Path)
$ErrorActionPreference="Stop"; Set-Location $RepoRoot
Push-Location .\libs\python\smartedu_cicd; try{python -m pytest -q} finally{Pop-Location}
python -m pytest -q .\tests\cicd
if(Get-Command docker -ErrorAction SilentlyContinue){$env:GRAFANA_ADMIN_PASSWORD="ci-test-only"; docker compose -f .\docker-compose.observability.yml config *> $null}
Write-Host "Sprint 22 local CI/CD self-checks passed."
