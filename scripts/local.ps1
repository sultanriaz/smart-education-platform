param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Configure','Infrastructure','Migrate','Services','Seed','Frontend','Test','Stop')]
    [string]$Action
)
$ErrorActionPreference = 'Stop'
$TaskRoot = Split-Path -Parent $PSScriptRoot
$TaskPython = Join-Path $TaskRoot '.venv/Scripts/python.exe'
Set-Location -LiteralPath $TaskRoot
function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed with exit code $LASTEXITCODE" }
}
function Invoke-Compose {
    param([string[]]$Arguments)
    Invoke-Checked 'docker' (@('compose','--project-name','smartedu-local','--env-file','.integration/runtime/infrastructure.env','-f','docker-compose.local.yml') + $Arguments)
}
switch ($Action) {
    'Configure' {
        if (!(Test-Path -LiteralPath $TaskPython)) { Invoke-Checked 'py' @('-3.12','-m','venv','.venv') }
        Invoke-Checked $TaskPython @('-m','pip','install','-r','requirements.integration.txt')
        Invoke-Checked $TaskPython @('scripts/configure_local.py')
        Push-Location 'apps/frontend'
        try { Invoke-Checked 'npm.cmd' @('ci') } finally { Pop-Location }
        Push-Location 'tests/e2e'
        try { Invoke-Checked 'npm.cmd' @('ci') } finally { Pop-Location }
    }
    'Infrastructure' { Invoke-Compose @('up','-d','--build','--wait','postgres','redis-cache','redis-durable','rabbitmq','minio','mailpit','api-gateway'); Invoke-Compose @('run','--build','--rm','minio-bootstrap') }
    'Migrate' { Invoke-Checked $TaskPython @('scripts/local_stack.py','migrate') }
    'Services' {
        Invoke-Checked $TaskPython @('scripts/local_stack.py','start')
        $TaskReady = $false
        for ($TaskAttempt=0; $TaskAttempt -lt 30; $TaskAttempt++) {
            & $TaskPython scripts/local_stack.py status
            if ($LASTEXITCODE -eq 0) { $TaskReady = $true; break }
            Start-Sleep -Seconds 2
        }
        if (!$TaskReady) { throw 'Readiness failed. Inspect .integration/runtime/*-api.log.' }
        Invoke-Checked $TaskPython @('scripts/local_stack.py','workers')
    }
    'Seed' { Invoke-Checked $TaskPython @('scripts/seed_local_demo.py') }
    'Frontend' {
        Push-Location 'apps/frontend'
        try { Invoke-Checked 'npm.cmd' @('run','build') } finally { Pop-Location }
        Invoke-Checked $TaskPython @('scripts/local_stack.py','frontend')
    }
    'Test' {
        Invoke-Checked $TaskPython @('scripts/verify_local.py')
        Push-Location 'apps/frontend'
        try {
            Invoke-Checked 'npm.cmd' @('run','lint')
            Invoke-Checked 'npm.cmd' @('run','test','--','--run')
            Invoke-Checked 'npm.cmd' @('run','build')
        } finally { Pop-Location }
        Invoke-Checked $TaskPython @('scripts/verify_live_local.py')
        Invoke-Checked $TaskPython @('scripts/run_local_e2e.py')
        Invoke-Checked 'node' @('apps/frontend/scripts/review-complete.cjs')
    }
    'Stop' { Invoke-Checked $TaskPython @('scripts/local_stack.py','stop'); Invoke-Compose @('down') }
}
