param(
    [ValidateSet("STAGING_ONLY")]
    [string]$Confirm,
    [string]$KubeContext = $env:STAGING_KUBE_CONTEXT,
    [string]$Namespace = "smartedu-staging",
    [int]$TimeoutSeconds = 300
)

$ErrorActionPreference = "Stop"

if ($Confirm -ne "STAGING_ONLY") {
    throw "Explicit -Confirm STAGING_ONLY is required."
}
if (-not $KubeContext) {
    throw "STAGING_KUBE_CONTEXT is required."
}
if ($KubeContext -match "(^|[-_/])(prod|production)([-_/]|$)") {
    throw "Refusing node drill against a production-looking context."
}

$Nodes = kubectl --context $KubeContext `
    get nodes `
    -o jsonpath='{range .items[*]}{.metadata.name}{"`n"}{end}'

$NodeList = @($Nodes -split "`n" | Where-Object { $_.Trim() })
if ($NodeList.Count -lt 2) {
    throw "At least two Kubernetes worker nodes are required for the node drill."
}

$Node = $NodeList[0].Trim()
Write-Host "Cordon/drain staging node: $Node"

kubectl --context $KubeContext cordon $Node

try {
    kubectl --context $KubeContext drain $Node `
        --ignore-daemonsets `
        --delete-emptydir-data `
        --grace-period=30 `
        "--timeout=${TimeoutSeconds}s"

    .\scripts\staging-rollout-status.ps1 `
        -KubeContext $KubeContext `
        -Namespace $Namespace `
        -TimeoutSeconds $TimeoutSeconds

    Write-Host "PASS application remained schedulable after staging node drain."
}
finally {
    kubectl --context $KubeContext uncordon $Node
}
