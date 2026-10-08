param(
    [Parameter(Mandatory=$true)]
    [string]$ReleaseManifest,
    [string]$RepoRoot = (Get-Location).Path,
    [string]$KubeContext = $env:STAGING_KUBE_CONTEXT,
    [string]$BaseUrl = $env:SMARTEDU_STAGING_URL,
    [int]$MigrationTimeoutSeconds = 300,
    [int]$RolloutTimeoutSeconds = 300
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if (-not $KubeContext) {
    throw "STAGING_KUBE_CONTEXT or -KubeContext is required."
}

$CurrentContext = (kubectl config current-context).Trim()
if ($CurrentContext -ne $KubeContext) {
    throw "Current kubectl context '$CurrentContext' does not match expected staging context '$KubeContext'."
}

if ($KubeContext -match "(^|[-_/])(prod|production)([-_/]|$)") {
    throw "Refusing to run staging deployment against a production-looking context: $KubeContext"
}

python .\scripts\staging-preflight.py `
    --release-manifest $ReleaseManifest

$Rendered = ".\deploy\kubernetes\rendered-staging.yaml"
$SplitDir = ".\deploy\kubernetes\rendered-staging"

python .\scripts\render-staging-release.py `
    $ReleaseManifest `
    --output $Rendered

python .\scripts\verify-staging-bundle.py $Rendered

if (Test-Path $SplitDir) {
    Remove-Item -Recurse -Force $SplitDir
}
python .\scripts\split-staging-bundle.py `
    $Rendered `
    --output-dir $SplitDir

Write-Host "=== Apply staging foundation ==="
kubectl --context $KubeContext apply -f "$SplitDir\01-foundation.yaml"

Write-Host "=== Verify staging secrets ==="
python .\scripts\staging-secret-check.py

$MigrationFile = "$SplitDir\02-migrations.yaml"
$MigrationContent = Get-Content $MigrationFile -Raw
if ($MigrationContent.Trim()) {
    Write-Host "=== Run migration jobs ==="

    kubectl --context $KubeContext `
        -n smartedu-staging `
        delete job `
        -l smartedu.io/job=migration `
        --ignore-not-found=true

    kubectl --context $KubeContext apply -f $MigrationFile

    $Jobs = kubectl --context $KubeContext `
        -n smartedu-staging `
        get jobs `
        -l smartedu.io/job=migration `
        -o jsonpath='{range .items[*]}{.metadata.name}{"`n"}{end}'

    foreach ($Job in ($Jobs -split "`n")) {
        if (-not $Job.Trim()) { continue }
        kubectl --context $KubeContext `
            -n smartedu-staging `
            wait `
            --for=condition=complete `
            "job/$($Job.Trim())" `
            "--timeout=${MigrationTimeoutSeconds}s"
    }
}
else {
    Write-Host "No migration jobs in this release."
}

Write-Host "=== Deploy staging application ==="
kubectl --context $KubeContext apply -f "$SplitDir\03-application.yaml"

$Deployments = kubectl --context $KubeContext `
    -n smartedu-staging `
    get deployment `
    -o jsonpath='{range .items[*]}{.metadata.name}{"`n"}{end}'

foreach ($Deployment in ($Deployments -split "`n")) {
    if (-not $Deployment.Trim()) { continue }
    kubectl --context $KubeContext `
        -n smartedu-staging `
        rollout status `
        "deployment/$($Deployment.Trim())" `
        "--timeout=${RolloutTimeoutSeconds}s"
}

if ($BaseUrl) {
    Write-Host "=== Public smoke ==="
    python .\scripts\staging-public-smoke.py --base-url $BaseUrl
}
else {
    Write-Warning "SMARTEDU_STAGING_URL not set; public smoke skipped."
}

Write-Host "Staging deployment completed."
