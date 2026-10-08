$ErrorActionPreference = "Stop"

$compose = ".\infra\gateway\tests\docker-compose.gateway-test.yml"

docker compose -f $compose up -d --build

try {
    Start-Sleep -Seconds 3

    $health = Invoke-RestMethod http://localhost:18080/health
    if ($health.status -ne "ok") { throw "Gateway health failed" }

    $routes = @(
        "identity/auth/login",
        "academic/courses",
        "attendance/sessions",
        "scheduling/timetable/me",
        "notifications/notifications",
        "facilities/facilities",
        "learning/resources",
        "assessments/quizzes",
        "reporting/dashboard/overview",
        "platform/search"
    )

    foreach ($route in $routes) {
        $response = Invoke-RestMethod `
            -Uri "http://localhost:18080/api/v1/$route" `
            -Headers @{ Authorization = "Bearer integration-test" }

        if (-not $response.request_id) {
            throw "Missing request ID for $route"
        }

        if ($response.path -notlike "/api/v1/*") {
            throw "Rewrite failed for $route -> $($response.path)"
        }
    }

    $preflight = Invoke-WebRequest `
        -Method OPTIONS `
        -Uri "http://localhost:18080/api/v1/academic/courses" `
        -Headers @{
            Origin = "http://localhost:5173"
            "Access-Control-Request-Method" = "GET"
        }

    if ($preflight.StatusCode -ne 204) {
        throw "CORS preflight failed"
    }

    Write-Host "Gateway integration smoke test passed."
}
finally {
    docker compose -f $compose down -v
}
