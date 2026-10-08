param(
    [ValidateSet(
        "identity-service",
        "academic-service",
        "attendance-service",
        "scheduling-service",
        "notification-service",
        "facility-service",
        "learning-service",
        "assessment-service",
        "reporting-service",
        "platform-service",
        "frontend",
        "api-gateway"
    )]
    [string]$Component = "attendance-service",
    [string]$KubeContext = $env:STAGING_KUBE_CONTEXT,
    [string]$Namespace = "smartedu-staging",
    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"

if (-not $KubeContext) {
    throw "STAGING_KUBE_CONTEXT is required."
}

$Before = kubectl --context $KubeContext `
    -n $Namespace `
    get deployment $Component `
    -o jsonpath='{.status.availableReplicas}'

if ([int]$Before -lt 2) {
    throw "$Component has fewer than 2 available replicas; refusing failure drill."
}

$Pod = kubectl --context $KubeContext `
    -n $Namespace `
    get pod `
    -l "smartedu.io/component=$Component" `
    -o jsonpath='{.items[0].metadata.name}'

if (-not $Pod) {
    throw "No pod found for $Component."
}

Write-Host "Deleting staging pod $Pod for $Component..."
kubectl --context $KubeContext -n $Namespace delete pod $Pod

kubectl --context $KubeContext `
    -n $Namespace `
    rollout status `
    "deployment/$Component" `
    "--timeout=${TimeoutSeconds}s"

$After = kubectl --context $KubeContext `
    -n $Namespace `
    get deployment $Component `
    -o jsonpath='{.status.availableReplicas}'

if ([int]$After -lt 2) {
    throw "$Component did not recover to >=2 available replicas."
}

Write-Host "PASS $Component recovered after pod deletion."
