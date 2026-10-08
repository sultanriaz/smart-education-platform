param(
    [string]$KubeContext = $env:PRODUCTION_KUBE_CONTEXT,
    [string]$Namespace = "smartedu",
    [string]$OutputDir = ".\launch\evidence\monitoring"
)

$ErrorActionPreference = "Stop"

if (-not $KubeContext) {
    throw "PRODUCTION_KUBE_CONTEXT is required."
}

New-Item -ItemType Directory -Force $OutputDir | Out-Null
$Stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")

kubectl --context $KubeContext `
    -n $Namespace `
    get deployment,pod,job,hpa,pdb,ingress `
    -o wide |
    Set-Content (Join-Path $OutputDir "kubernetes-$Stamp.txt")

kubectl --context $KubeContext `
    -n $Namespace `
    get events `
    --sort-by=.lastTimestamp |
    Select-Object -Last 200 |
    Set-Content (Join-Path $OutputDir "events-$Stamp.txt")

Write-Host "Saved production Kubernetes monitoring snapshot at $Stamp."
