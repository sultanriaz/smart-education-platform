param(
    [string]$RepoRoot = (Get-Location).Path,
    [switch]$Exporters
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

$Args = @("compose", "-f", ".\docker-compose.observability.yml")
if ($Exporters) {
    $Args += @("-f", ".\docker-compose.observability.exporters.yml")
}
$Args += @("--env-file", ".\.env.observability", "down")

docker @Args
