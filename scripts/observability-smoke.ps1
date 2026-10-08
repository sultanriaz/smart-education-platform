param(
    [switch]$RequireServices
)

$ErrorActionPreference = "Stop"

$Args = @(".\scripts\verify-observability.py")
if ($RequireServices) {
    $Args += "--require-services"
}

python @Args
