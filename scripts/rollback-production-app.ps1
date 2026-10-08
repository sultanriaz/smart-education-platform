param(
    [Parameter(Mandatory=$true)]
    [string]$PreviousReleaseManifest,

    [Parameter(Mandatory=$true)]
    [string]$CurrentReleaseManifest,

    [ValidateSet("PRODUCTION_ROLLBACK")]
    [string]$Confirm,

    [ValidateSet("SCHEMA_COMPATIBLE")]
    [string]$SchemaCompatibility,

    [string]$RepoRoot = (Get-Location).Path,
    [string]$KubeContext = $env:PRODUCTION_KUBE_CONTEXT,
    [int]$RolloutTimeoutSeconds = 600
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if ($Confirm -ne "PRODUCTION_ROLLBACK") {
    throw "Explicit -Confirm PRODUCTION_ROLLBACK is required."
}
if ($SchemaCompatibility -ne "SCHEMA_COMPATIBLE") {
    throw "Explicit -SchemaCompatibility SCHEMA_COMPATIBLE is required. This script never downgrades the database."
}
if (-not $KubeContext) {
    throw "PRODUCTION_KUBE_CONTEXT is required."
}

$CurrentContext = (kubectl config current-context).Trim()
if ($CurrentContext -ne $KubeContext) {
    throw "Current kubectl context '$CurrentContext' does not match expected production context '$KubeContext'."
}

Write-Host "Current release manifest retained for audit: $CurrentReleaseManifest"
Write-Host "Previous release manifest selected for application-only rollback: $PreviousReleaseManifest"

$PreviousBundle = ".\deploy\kubernetes\rollback-previous-production.yaml"
$PreviousDeployments = ".\deploy\kubernetes\rollback-previous-deployments.yaml"

Write-Host "=== Render previous digest-pinned release ==="
python .\scripts\render-k8s-release.py `
    $PreviousReleaseManifest `
    --output $PreviousBundle

python .\scripts\verify-production-bundle.py $PreviousBundle

python .\scripts\extract-deployments.py `
    $PreviousBundle `
    --output $PreviousDeployments

Write-Host "=== APPLICATION-ONLY rollback ==="
Write-Host "No Alembic downgrade will be executed."

kubectl --context $KubeContext apply -f $PreviousDeployments

$Deployments = kubectl --context $KubeContext `
    -n smartedu `
    get deployment `
    -o jsonpath='{range .items[*]}{.metadata.name}{"`n"}{end}'

foreach ($Deployment in ($Deployments -split "`n")) {
    if (-not $Deployment.Trim()) { continue }

    kubectl --context $KubeContext `
        -n smartedu `
        rollout status `
        "deployment/$($Deployment.Trim())" `
        "--timeout=${RolloutTimeoutSeconds}s"
}

Write-Host "Application rollback completed."
Write-Host "Run production smoke, role smoke, event smoke, and observability checks immediately."
