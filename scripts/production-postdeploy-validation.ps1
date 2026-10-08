param(
    [Parameter(Mandatory=$true)]
    [string]$LaunchRecord,

    [ValidateSet("PRODUCTION_SAFE_VALIDATION")]
    [string]$Confirm,

    [string]$RepoRoot = (Get-Location).Path,
    [string]$ProductionUrl = $env:SMARTEDU_PRODUCTION_URL,
    [string]$RoleSmokeScript = $env:PRODUCTION_ROLE_SMOKE_SCRIPT,
    [string]$EventSmokeScript = $env:PRODUCTION_EVENT_SMOKE_SCRIPT,
    [string]$ObservabilityScript = $env:PRODUCTION_OBSERVABILITY_CHECK_SCRIPT
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if ($Confirm -ne "PRODUCTION_SAFE_VALIDATION") {
    throw "Explicit -Confirm PRODUCTION_SAFE_VALIDATION is required."
}
if (-not $ProductionUrl) {
    throw "SMARTEDU_PRODUCTION_URL or -ProductionUrl is required."
}

foreach ($Pair in @(
    @("role-smoke", $RoleSmokeScript),
    @("event-smoke", $EventSmokeScript),
    @("observability", $ObservabilityScript)
)) {
    $Phase = $Pair[0]
    $Script = $Pair[1]

    if (-not $Script) {
        throw "$Phase hook is not configured."
    }
    if (-not (Test-Path $Script)) {
        throw "$Phase hook does not exist: $Script"
    }

    python .\scripts\record-launch-phase.py `
        $LaunchRecord `
        $Phase `
        --status IN_PROGRESS `
        --operator $env:USERNAME

    & $Script
    if ($LASTEXITCODE -ne 0) {
        python .\scripts\record-launch-phase.py `
            $LaunchRecord `
            $Phase `
            --status FAIL `
            --operator $env:USERNAME `
            --notes "$Phase production-safe validation failed."
        throw "$Phase production-safe validation failed."
    }

    python .\scripts\record-launch-phase.py `
        $LaunchRecord `
        $Phase `
        --status PASS `
        --operator $env:USERNAME
}

Write-Host "PASS production role/event/observability validation hooks."
