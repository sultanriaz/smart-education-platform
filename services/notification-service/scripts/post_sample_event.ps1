param(
    [string]$BaseUrl = "http://localhost:8005",
    [string]$InternalToken = "CHANGE_ME_INTERNAL_EVENT_TOKEN",
    [Parameter(Mandatory=$true)][string]$StudentUserId
)

$body = @{
    event_id = [guid]::NewGuid().ToString()
    source_service = "attendance-service"
    event_type = "attendance.low_attendance_detected"
    payload = @{
        student_user_id = $StudentUserId
        title = "Attendance warning"
        message = "Your attendance has fallen below the configured threshold."
        category = "attendance"
        priority = "HIGH"
    }
    targets = @{
        user_ids = @($StudentUserId)
    }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
    -Method POST `
    -Uri "$BaseUrl/api/v1/internal/events" `
    -Headers @{"X-Internal-Token"=$InternalToken} `
    -ContentType "application/json" `
    -Body $body
