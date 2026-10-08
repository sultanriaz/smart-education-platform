param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$ReleaseManifest = ""
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "=== smartedu-staging package ==="
Push-Location .\libs\python\smartedu_staging
try {
    python -m pytest -q
}
finally {
    Pop-Location
}

Write-Host "`n=== Staging manifest/config tests ==="
python -m pytest -q .\tests\staging

Write-Host "`n=== Staging preflight ==="
$Args = @(".\scripts\staging-preflight.py")
if ($ReleaseManifest) {
    $Args += @("--release-manifest", $ReleaseManifest)
}
python @Args

if ($ReleaseManifest) {
    $Output = ".\deploy\kubernetes\rendered-staging.yaml"

    Write-Host "`n=== Render staging release ==="
    python .\scripts\render-staging-release.py `
        $ReleaseManifest `
        --output $Output

    Write-Host "`n=== Verify staging bundle ==="
    python .\scripts\verify-staging-bundle.py $Output
}

Write-Host "`nSprint 24 offline checks completed."
