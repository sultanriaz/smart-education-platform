param(
    [string]$RepoRoot = (Get-Location).Path,
    [switch]$Redis,
    [switch]$RabbitMQ,
    [switch]$ObjectStorage
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if (-not ($Redis -or $RabbitMQ -or $ObjectStorage)) {
    $Redis = $true
    $RabbitMQ = $true
    $ObjectStorage = $true
}

if ($Redis) {
    Write-Host "`n=== Redis benchmark ==="
    python .\infra\performance\redis\benchmark.py
}

if ($RabbitMQ) {
    Write-Host "`n=== RabbitMQ benchmark ==="
    python .\infra\performance\rabbitmq\benchmark.py
}

if ($ObjectStorage) {
    Write-Host "`n=== Object-storage benchmark ==="
    python .\infra\performance\minio\benchmark.py
}
