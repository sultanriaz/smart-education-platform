$ErrorActionPreference = "Stop"

$networkName = "smart-education-edge"

$existing = docker network ls --filter "name=^${networkName}$" --format "{{.Name}}"

if ($existing -ne $networkName) {
    docker network create $networkName | Out-Null
    Write-Host "Created Docker network: $networkName"
}
else {
    Write-Host "Docker network already exists: $networkName"
}
