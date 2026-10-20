#Requires -Version 5.1
<#
.SYNOPSIS
  Windows dev: Docker for Redis + MinIO + Mailpit; PostgreSQL on the host.

.DESCRIPTION
  Separate from scripts/local-dev.ps1 (all-native infra).

  Prerequisites:
    - Docker Desktop (WSL2 backend recommended)
    - PostgreSQL 16+ with pgvector on Windows (local service)
    - Python 3.12+, uv, Node 22+, pnpm 9.15.4

  Quick start (repo root):
    .\scripts\local-dev-docker.ps1 bootstrap
    .\scripts\local-dev-docker.ps1 api      # terminal 1
    .\scripts\local-dev-docker.ps1 web      # terminal 2
#>
param(
    [Parameter(Position = 0)]
    [ValidateSet(
        'help',
        'commands',
        'docker-up',
        'docker-down',
        'docker-logs',
        'docker-ps',
        'install',
        'env',
        'migrate',
        'seed',
        'setup-db',
        'bootstrap',
        'api',
        'web',
        'worker'
    )]
    [string]$Action = 'help',

    [string]$AdminEmail = 'admin@localhost',
    [string]$AdminPassword = 'ChangeMeNow123!'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path $PSScriptRoot -Parent
$ComposeFile = Join-Path $RepoRoot 'docker\compose.deps.yaml'
$PostgresInitSql = Join-Path $RepoRoot 'docker\postgres-init.sql'

$Paths = @{
    AiPlatform = Join-Path $RepoRoot 'ai-platform'
    Backend    = Join-Path $RepoRoot 'backend'
    Frontend   = Join-Path $RepoRoot 'frontend'
    WebApp     = Join-Path $RepoRoot 'frontend\apps\web'
}

function Write-Title([string]$Text) {
    Write-Host ''
    Write-Host "=== $Text ===" -ForegroundColor Cyan
}

function Assert-Docker {
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $docker) {
        throw 'Docker not found. Install Docker Desktop and ensure docker is on PATH.'
    }
    docker version | Out-Null
}

function Invoke-Compose {
    param([string[]]$ComposeArgs)
    Assert-Docker
    if (-not (Test-Path -LiteralPath $ComposeFile)) {
        throw "Missing compose file: $ComposeFile"
    }
    & docker compose -f $ComposeFile @ComposeArgs
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose failed (exit $LASTEXITCODE)"
    }
}

function Assert-Dir([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing $Label folder: $Path"
    }
}

function Invoke-InDir {
    param(
        [string]$Directory,
        [scriptblock]$Script
    )
    Push-Location -LiteralPath $Directory
    try {
        & $Script
    }
    finally {
        Pop-Location
    }
}

function Start-DockerDeps {
    Write-Title 'Docker: Redis, MinIO (+ bucket sales-agent), Mailpit'
    Invoke-Compose @('up', '-d')
    Write-Host 'Services:' -ForegroundColor Green
    Write-Host '  Redis     redis://localhost:6379/0'
    Write-Host '  MinIO API http://localhost:9000  (console http://localhost:9001)'
    Write-Host '  Mailpit   SMTP localhost:1025  UI http://localhost:8025'
    Write-Host 'PostgreSQL: local Windows install -> localhost:5432 (not in Docker)'
}

function Stop-DockerDeps {
    Write-Title 'Stop Docker dev dependencies'
    Invoke-Compose @('down')
}

function Show-DockerPs {
    Write-Title 'Docker compose status'
    Invoke-Compose @('ps')
}

function Tail-DockerLogs {
    Write-Title 'Docker logs (Ctrl+C to exit)'
    Invoke-Compose @('logs', '-f', '--tail', '100')
}

function Install-Packages {
    Write-Title 'Install Python + Node packages'
    Assert-Dir $Paths.AiPlatform 'ai-platform'
    Assert-Dir $Paths.Backend 'backend'
    Assert-Dir $Paths.Frontend 'frontend'

    Invoke-InDir $Paths.AiPlatform { uv sync }
    Invoke-InDir $Paths.Backend { uv sync }
    Invoke-InDir $Paths.Frontend {
        corepack enable | Out-Null
        corepack prepare pnpm@9.15.4 --activate | Out-Null
        pnpm install
    }
    Write-Host 'Packages installed.' -ForegroundColor Green
}

function Copy-EnvFiles {
    Write-Title 'Env files (matches Docker deps + local Postgres)'
    $backendEnv = Join-Path $Paths.Backend '.env'
    $backendExample = Join-Path $Paths.Backend '.env.example'
    $webEnv = Join-Path $Paths.WebApp '.env.local'
    $webExample = Join-Path $Paths.WebApp '.env.example'

    if (-not (Test-Path -LiteralPath $backendEnv)) {
        Copy-Item -LiteralPath $backendExample -Destination $backendEnv
        Write-Host 'Created backend\.env'
    }
    else {
        Write-Host 'backend\.env already exists (unchanged)'
    }

    if (-not (Test-Path -LiteralPath $webEnv)) {
        Copy-Item -LiteralPath $webExample -Destination $webEnv
        Write-Host 'Created frontend\apps\web\.env.local'
    }
    else {
        Write-Host 'frontend\apps\web\.env.local already exists (unchanged)'
    }

    Write-Host @'

Ensure backend\.env uses (default from .env.example):
  DATABASE_URL=postgresql+asyncpg://sales_agent:sales_agent@localhost:5432/sales_agent
  REDIS_URL=redis://localhost:6379/0
  S3_ENDPOINT_URL=http://localhost:9000
  SMTP_HOST=localhost
  SMTP_PORT=1025
  AI_PLATFORM_MODE=in_process
'@ -ForegroundColor DarkGray
}

function Show-PostgresInstructions {
    Write-Title 'Local PostgreSQL (run once or to reset DB)'
    Write-Host "SQL file: $PostgresInitSql" -ForegroundColor DarkGray
    Write-Host @'

Example (adjust psql path / superuser):
  psql -U postgres -f docker\postgres-init.sql

Or open docker\postgres-init.sql in pgAdmin / DBeaver and execute as superuser.

Then from repo root:
  .\scripts\local-dev-docker.ps1 setup-db
'@ -ForegroundColor Yellow
}

function Run-Migrate {
    Write-Title 'Alembic migrations (backend folder)'
    Invoke-InDir $Paths.Backend { uv run alembic upgrade head }
    Write-Host 'Migrations applied.' -ForegroundColor Green
}

function Run-Seed {
    Write-Title 'Seed platform data + super admin (backend folder)'
    $email = $AdminEmail
    $password = $AdminPassword
    Invoke-InDir $Paths.Backend {
        uv run python -m app.main.cli seed
        uv run python -m app.main.cli seed-super-admin --email $email --password $password
    }
    Write-Host "Super admin: $AdminEmail" -ForegroundColor Green
}

function Run-Bootstrap {
    Install-Packages
    Copy-EnvFiles
    Start-DockerDeps
    Show-PostgresInstructions
    Write-Host ''
    Write-Host 'After PostgreSQL is ready, run:' -ForegroundColor Yellow
    Write-Host '  .\scripts\local-dev-docker.ps1 setup-db' -ForegroundColor Yellow
    Write-Host '  .\scripts\local-dev-docker.ps1 api' -ForegroundColor Yellow
    Write-Host '  .\scripts\local-dev-docker.ps1 web' -ForegroundColor Yellow
}

function Start-Api {
    Write-Title 'Backend API — folder: backend'
    Write-Host 'http://localhost:8000/api/v1/docs' -ForegroundColor DarkGray
    Invoke-InDir $Paths.Backend {
        uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src
    }
}

function Start-Web {
    Write-Title 'Frontend — folder: frontend\apps\web'
    Write-Host 'http://localhost:3000' -ForegroundColor DarkGray
    Invoke-InDir $Paths.WebApp { pnpm dev }
}

function Start-Worker {
    Write-Title 'ARQ worker — folder: backend'
    Invoke-InDir $Paths.Backend {
        uv run arq app.workers.arq_settings.WorkerSettings
    }
}

function Show-Commands {
    Write-Title 'Windows + Docker deps + local PostgreSQL'
    @"

REPO ROOT: $RepoRoot

--- Docker (Redis, MinIO, Mailpit) — NOT PostgreSQL ---
  docker compose -f docker\compose.deps.yaml up -d
  docker compose -f docker\compose.deps.yaml ps
  docker compose -f docker\compose.deps.yaml logs -f
  docker compose -f docker\compose.deps.yaml down

  Or:
  .\scripts\local-dev-docker.ps1 docker-up
  .\scripts\local-dev-docker.ps1 docker-ps
  .\scripts\local-dev-docker.ps1 docker-down

--- Local PostgreSQL 16 + pgvector (Windows host) ---
  psql -U postgres -f docker\postgres-init.sql

  DATABASE_URL=postgresql+asyncpg://sales_agent:sales_agent@localhost:5432/sales_agent

--- Packages (folder order) ---
  cd $RepoRoot\ai-platform && uv sync
  cd $RepoRoot\backend && uv sync
  cd $RepoRoot\frontend && corepack enable && corepack prepare pnpm@9.15.4 --activate && pnpm install

--- Env ---
  Copy-Item $RepoRoot\backend\.env.example $RepoRoot\backend\.env
  Copy-Item $RepoRoot\frontend\apps\web\.env.example $RepoRoot\frontend\apps\web\.env.local

--- Migrations + seed (cd backend) ---
  uv run alembic upgrade head
  uv run python -m app.main.cli seed
  uv run python -m app.main.cli seed-super-admin --email admin@localhost --password "ChangeMeNow123!"

--- Run app (native, not in Docker) ---
  cd $RepoRoot\backend
  uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src

  cd $RepoRoot\frontend\apps\web
  pnpm dev

--- Fresh tenant ---
  Login http://localhost:3000/en/login (admin@localhost / ChangeMeNow123!)
  Seller dashboard -> create workspace

--- AI ---
  No separate container; AI_PLATFORM_MODE=in_process in backend\.env

"@ | Write-Host
}

function Show-Help {
    Show-Commands
    Write-Host @'

Script shortcuts (repo root):
  .\scripts\local-dev-docker.ps1 bootstrap    # install + env + docker-up + PG instructions
  .\scripts\local-dev-docker.ps1 docker-up    # start Redis, MinIO, Mailpit
  .\scripts\local-dev-docker.ps1 docker-down
  .\scripts\local-dev-docker.ps1 setup-db     # migrate + seed (Postgres must be up)
  .\scripts\local-dev-docker.ps1 api
  .\scripts\local-dev-docker.ps1 web
  .\scripts\local-dev-docker.ps1 commands

All-native infra (no Docker): scripts\local-dev.ps1
Full docs: docs\LOCAL_SETUP.md
'@ -ForegroundColor Yellow
}

switch ($Action) {
    'help' { Show-Help }
    'commands' { Show-Commands }
    'docker-up' { Start-DockerDeps }
    'docker-down' { Stop-DockerDeps }
    'docker-logs' { Tail-DockerLogs }
    'docker-ps' { Show-DockerPs }
    'install' { Install-Packages }
    'env' { Copy-EnvFiles }
    'migrate' { Run-Migrate }
    'seed' { Run-Seed }
    'setup-db' {
        Run-Migrate
        Run-Seed
    }
    'bootstrap' { Run-Bootstrap }
    'api' { Start-Api }
    'web' { Start-Web }
    'worker' { Start-Worker }
}
