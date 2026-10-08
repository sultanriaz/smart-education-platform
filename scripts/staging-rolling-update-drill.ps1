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
    [string]$Component = "api-gateway",
    [string]$KubeContext = $env:STAGING_KUBE_CONTEXT,
    [string]$Namespace = "smartedu-staging",
    [int]$TimeoutSeconds = 300
)

$ErrorActionPreference = "Stop"
if (-not $KubeContext) { throw "STAGING_KUBE_CONTEXT is required." }

$BeforeUnavailable = kubectl --context $KubeContext `
    -n $Namespace `
    get deployment $Component `
    -o jsonpath='{.spec.strategy.rollingUpdate.maxUnavailable}'

if ($BeforeUnavailable -ne "0") {
    throw "$Component maxUnavailable must be 0 for this drill."
}

kubectl --context $KubeContext `
    -n $Namespace `
    rollout restart `
    "deployment/$Component"

kubectl --context $KubeContext `
    -n $Namespace `
    rollout status `
    "deployment/$Component" `
    "--timeout=${TimeoutSeconds}s"

Write-Host "PASS $Component completed a rolling restart."
