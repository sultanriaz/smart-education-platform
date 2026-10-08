param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$EnvFile = ".env.infrastructure"
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

$Args = @("-f", "docker-compose.infrastructure.yml")
if (Test-Path $EnvFile) {
    $Args += @("--env-file", $EnvFile)
}

docker compose @Args up -d

docker compose @Args ps
