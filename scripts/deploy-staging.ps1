param([Parameter(Mandatory=$true)][string]$Manifest,[string]$RepoRoot=(Get-Location).Path,[string]$EnvironmentFile=".env.staging")
$ErrorActionPreference="Stop"; Set-Location $RepoRoot
if(-not(Test-Path $Manifest)){throw "Manifest not found"}; if(-not(Test-Path $EnvironmentFile)){throw "Staging env not found"}; if(-not $env:STAGING_COMPOSE_FILES){throw "STAGING_COMPOSE_FILES is required"}
python .\scripts\validate-release-manifest.py $Manifest
python .\scripts\render-release-env.py $Manifest --output .\.env.release
$Compose=@("compose"); foreach($f in ($env:STAGING_COMPOSE_FILES -split ";")){if(-not(Test-Path $f)){throw "Compose file not found: $f"}; $Compose+=@("-f",$f)}; $Compose+=@("--env-file",$EnvironmentFile,"--env-file",".\.env.release")
$DeployDir=Join-Path $RepoRoot ".deployments"; New-Item -ItemType Directory -Force -Path $DeployDir|Out-Null; $Current=Join-Path $DeployDir "current-release.json"; $Previous=Join-Path $DeployDir "previous-release.json"; if(Test-Path $Current){Copy-Item $Current $Previous -Force}
if($env:STAGING_BACKUP_SCRIPT){if(-not(Test-Path $env:STAGING_BACKUP_SCRIPT)){throw "Backup script missing"}; & $env:STAGING_BACKUP_SCRIPT; if($LASTEXITCODE -ne 0){throw "Backup failed"}}
docker @($Compose+@("pull")); if($LASTEXITCODE -ne 0){throw "pull failed"}
$Release=Get-Content $Manifest -Raw|ConvertFrom-Json
foreach($Component in $Release.migration_components){$Service=(python -c "from smartedu_cicd import load_catalog;c=load_catalog('config/cicd/components.yaml');m={x.name:x for x in c.components};print(m['$Component'].deploy_service or m['$Component'].name)").Trim(); docker @($Compose+@("run","--rm",$Service,"python","-m","alembic","-c","alembic.ini","upgrade","head")); if($LASTEXITCODE -ne 0){throw "Migration failed: $Component"}}
docker @($Compose+@("up","-d","--remove-orphans")); if($LASTEXITCODE -ne 0){throw "deploy failed"}; if(-not $env:STAGING_HEALTH_URL){throw "STAGING_HEALTH_URL required"}; python .\scripts\wait-for-health.py $env:STAGING_HEALTH_URL --timeout 180; if($LASTEXITCODE -ne 0){throw "health failed"}; Copy-Item $Manifest $Current -Force
