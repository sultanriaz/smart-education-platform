param(
    [string]$KubeContext = $env:STAGING_KUBE_CONTEXT,
    [string]$Namespace = "smartedu-staging",
    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"

if (-not $KubeContext) {
    throw "STAGING_KUBE_CONTEXT is required."
}

$Deployments = kubectl --context $KubeContext `
    -n $Namespace `
    get deployment `
    -o jsonpath='{range .items[*]}{.metadata.name}{"`n"}{end}'

foreach ($Deployment in ($Deployments -split "`n")) {
    if (-not $Deployment.Trim()) { continue }
    kubectl --context $KubeContext `
        -n $Namespace `
        rollout status `
        "deployment/$($Deployment.Trim())" `
        "--timeout=${TimeoutSeconds}s"
}

Write-Host "All staging deployments rolled out successfully."
