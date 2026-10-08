param(
    [string]$KubeContext = $env:PRODUCTION_KUBE_CONTEXT,
    [string]$Namespace = "smartedu",
    [int]$TimeoutSeconds = 300
)

$ErrorActionPreference = "Stop"
if (-not $KubeContext) {
    throw "PRODUCTION_KUBE_CONTEXT is required."
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

kubectl --context $KubeContext `
    -n $Namespace `
    get deployment,pod,job,hpa,pdb,ingress `
    -o wide
