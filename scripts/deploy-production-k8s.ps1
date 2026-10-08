param(
    [Parameter(Mandatory=$true)]
    [string]$ReleaseManifest,

    [Parameter(Mandatory=$true)]
    [string]$ReadinessRun,

    [ValidateSet("PRODUCTION_DEPLOY")]
    [string]$Confirm,

    [string]$RepoRoot = (Get-Location).Path,
    [string]$KubeContext = $env:PRODUCTION_KUBE_CONTEXT,
    [string]$ProductionUrl = $env:SMARTEDU_PRODUCTION_URL,
    [string]$AcceptedReleaseManifest = $env:SMARTEDU_ACCEPTED_RELEASE_MANIFEST,
    [string]$BackupScript = $env:PRODUCTION_BACKUP_SCRIPT,
    [string]$LaunchRecord = ".\launch\current-launch.json",
    [int]$MigrationTimeoutSeconds = 600,
    [int]$RolloutTimeoutSeconds = 600
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if ($Confirm -ne "PRODUCTION_DEPLOY") {
    throw "Explicit -Confirm PRODUCTION_DEPLOY is required."
}
if (-not $KubeContext) {
    throw "PRODUCTION_KUBE_CONTEXT or -KubeContext is required."
}
if (-not $ProductionUrl) {
    throw "SMARTEDU_PRODUCTION_URL or -ProductionUrl is required."
}
if (-not $BackupScript) {
    throw "PRODUCTION_BACKUP_SCRIPT is required. Production launch cannot proceed without a backup/PITR checkpoint."
}
if (-not (Test-Path $BackupScript)) {
    throw "Configured backup script does not exist: $BackupScript"
}

$CurrentContext = (kubectl config current-context).Trim()
if ($CurrentContext -ne $KubeContext) {
    throw "Current kubectl context '$CurrentContext' does not match expected production context '$KubeContext'."
}

Write-Host "=== Production launch preflight ==="
$PreflightArgs = @(
    ".\scripts\production-launch-preflight.py",
    $ReleaseManifest,
    "--readiness-run", $ReadinessRun,
    "--production-url", $ProductionUrl
)
if ($AcceptedReleaseManifest) {
    $PreflightArgs += @(
        "--accepted-release-manifest", $AcceptedReleaseManifest
    )
}
python @PreflightArgs

if (-not (Test-Path .\scripts\render-k8s-release.py)) {
    throw "Sprint 23 render-k8s-release.py not found."
}
if (-not (Test-Path .\scripts\verify-k8s-bundle.py)) {
    throw "Sprint 23 verify-k8s-bundle.py not found."
}

$Rendered = ".\deploy\kubernetes\rendered-production.yaml"
$SplitDir = ".\deploy\kubernetes\rendered-production"
$MigrationBundle = ".\deploy\kubernetes\production-launch\migrations.yaml"

New-Item -ItemType Directory -Force `
    (Split-Path $Rendered -Parent) | Out-Null
New-Item -ItemType Directory -Force `
    (Split-Path $MigrationBundle -Parent) | Out-Null
New-Item -ItemType Directory -Force `
    (Split-Path $LaunchRecord -Parent) | Out-Null

Write-Host "=== Render immutable production bundle ==="
python .\scripts\render-k8s-release.py `
    $ReleaseManifest `
    --output $Rendered

python .\scripts\verify-k8s-bundle.py $Rendered
python .\scripts\verify-production-bundle.py $Rendered

Write-Host "=== Render production migration Jobs ==="
python .\scripts\render-production-migrations.py `
    $ReleaseManifest `
    --output $MigrationBundle

python .\scripts\verify-production-migrations.py `
    $ReleaseManifest `
    $MigrationBundle

if (Test-Path $SplitDir) {
    Remove-Item -Recurse -Force $SplitDir
}
python .\scripts\split-production-bundle.py `
    $Rendered `
    --output-dir $SplitDir

Write-Host "=== Initialize launch evidence record ==="
if (-not (Test-Path $LaunchRecord)) {
    python .\scripts\initialize-launch-record.py `
        $ReleaseManifest `
        --readiness-run $ReadinessRun `
        --production-url $ProductionUrl `
        --kube-context $KubeContext `
        --output $LaunchRecord
}

python .\scripts\record-launch-phase.py `
    $LaunchRecord `
    preflight `
    --status PASS `
    --operator $env:USERNAME `
    --evidence $Rendered

Write-Host "=== Apply production foundation ==="
kubectl --context $KubeContext apply -f "$SplitDir\01-foundation.yaml"

Write-Host "=== Verify required production Secrets already exist ==="
if (Test-Path .\scripts\production-secret-check.py) {
    python .\scripts\production-secret-check.py
}
else {
    Write-Warning "production-secret-check.py not found; Codex must reconcile this to the actual production secret mechanism before launch."
}

Write-Host "=== Create/confirm production recovery point ==="
python .\scripts\record-launch-phase.py `
    $LaunchRecord `
    backup `
    --status IN_PROGRESS `
    --operator $env:USERNAME

$BackupOutput = & $BackupScript 2>&1
if ($LASTEXITCODE -ne 0) {
    python .\scripts\record-launch-phase.py `
        $LaunchRecord `
        backup `
        --status FAIL `
        --operator $env:USERNAME `
        --notes "Production backup/PITR hook failed."
    throw "Production backup/PITR checkpoint failed."
}

$BackupReference = ($BackupOutput | Select-Object -Last 1).ToString().Trim()
if (-not $BackupReference) {
    throw "Backup script did not return a backup/PITR reference on its final output line."
}

python .\scripts\record-launch-phase.py `
    $LaunchRecord `
    backup `
    --status PASS `
    --operator $env:USERNAME `
    --notes "backup_reference=$BackupReference"

python .\scripts\record-launch-backup-reference.py `
    $LaunchRecord `
    $BackupReference

Write-Host "=== Execute release migration Jobs ==="
python .\scripts\record-launch-phase.py `
    $LaunchRecord `
    migrations `
    --status IN_PROGRESS `
    --operator $env:USERNAME

python .\scripts\run-production-migrations.py `
    $MigrationBundle `
    --context $KubeContext `
    --namespace smartedu `
    --timeout-seconds $MigrationTimeoutSeconds

python .\scripts\record-launch-phase.py `
    $LaunchRecord `
    migrations `
    --status PASS `
    --operator $env:USERNAME `
    --evidence $MigrationBundle

Write-Host "=== Deploy application resources ==="
python .\scripts\record-launch-phase.py `
    $LaunchRecord `
    application-rollout `
    --status IN_PROGRESS `
    --operator $env:USERNAME

kubectl --context $KubeContext apply -f "$SplitDir\03-application.yaml"

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

python .\scripts\record-launch-phase.py `
    $LaunchRecord `
    application-rollout `
    --status PASS `
    --operator $env:USERNAME `
    --evidence "$SplitDir\03-application.yaml"

Write-Host "=== Production public smoke ==="
python .\scripts\record-launch-phase.py `
    $LaunchRecord `
    public-smoke `
    --status IN_PROGRESS `
    --operator $env:USERNAME

python .\scripts\production-public-smoke.py `
    --base-url $ProductionUrl

python .\scripts\record-launch-phase.py `
    $LaunchRecord `
    public-smoke `
    --status PASS `
    --operator $env:USERNAME

Write-Host ""
Write-Host "Automated rollout steps completed."
Write-Host "DO NOT mark the launch SUCCEEDED yet."
Write-Host "Complete role-smoke, event-smoke, observability, and launch monitoring first."
Write-Host "Launch record: $LaunchRecord"
Write-Host "Backup reference: $BackupReference"
