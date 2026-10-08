param(
    [ValidateSet("smoke","baseline","srs-500","stress-750","stress-1000","soak-250")]
    [string]$Profile = "smoke",
    [string]$HostUrl = $env:SMARTEDU_GATEWAY_URL,
    [string]$RepoRoot = (Get-Location).Path,
    [string]$ResultName = ""
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if (-not $HostUrl) {
    throw "SMARTEDU_GATEWAY_URL or -HostUrl is required."
}

$Users = python .\scripts\load-profile.py $Profile --field users
$SpawnRate = python .\scripts\load-profile.py $Profile --field spawn_rate
$Duration = python .\scripts\load-profile.py $Profile --field duration_seconds

if (-not $ResultName) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $ResultName = "$Profile-$Stamp"
}

$OutputRoot = Join-Path $RepoRoot "tests\performance\results\$ResultName"
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$CsvPrefix = Join-Path $OutputRoot "locust"

Write-Host "Profile=$Profile users=$Users spawn_rate=$SpawnRate duration=${Duration}s"
Write-Host "Target=$HostUrl"

Push-Location .\tests\performance\locust
try {
    locust `
        -f .\locustfile.py `
        --headless `
        --host $HostUrl `
        -u $Users `
        -r $SpawnRate `
        -t "${Duration}s" `
        --csv $CsvPrefix `
        --csv-full-history
}
finally {
    Pop-Location
}

$StatsFile = "${CsvPrefix}_stats.csv"
python .\scripts\evaluate-performance.py `
    $StatsFile `
    --output (Join-Path $OutputRoot "evaluation.json")

Write-Host "Performance artifacts: $OutputRoot"
