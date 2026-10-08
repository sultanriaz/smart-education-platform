param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$ReleaseManifest = ""
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "=== smartedu-deploy ==="
Push-Location .\libs\python\smartedu_deploy
try {
    python -m pytest -q
}
finally {
    Pop-Location
}

Write-Host "`n=== Deployment manifest tests ==="
python -m pytest -q .\tests\deployment

Write-Host "`n=== Production topology preflight ==="
$Args = @(".\scripts\preflight-production.py")
if ($ReleaseManifest) {
    $Args += @("--release-manifest", $ReleaseManifest)
}
python @Args

if ($ReleaseManifest) {
    $Output = ".\deploy\kubernetes\rendered-production.yaml"
    Write-Host "`n=== Render immutable production bundle ==="
    python .\scripts\render-k8s-release.py `
        $ReleaseManifest `
        --output $Output

    python .\scripts\verify-k8s-bundle.py $Output
}
