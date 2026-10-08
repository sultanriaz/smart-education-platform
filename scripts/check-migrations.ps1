param([string]$RepoRoot=(Get-Location).Path)
$ErrorActionPreference="Stop"; Set-Location $RepoRoot
$Services=Get-ChildItem .\services -Directory|Where-Object{Test-Path (Join-Path $_.FullName "alembic.ini")}|Sort-Object Name
foreach($Service in $Services){Push-Location $Service.FullName; try{$Heads=@(python -m alembic -c alembic.ini heads|Where-Object{$_.Trim()}); if($Heads.Count -ne 1){throw "$($Service.Name): expected one Alembic head"}; python -m alembic -c alembic.ini check; if($LASTEXITCODE -ne 0){throw "$($Service.Name): drift check failed"}} finally{Pop-Location}}
