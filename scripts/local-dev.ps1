#Requires -Version 5.1
<#
.SYNOPSIS
  Local dev commands for AI_Business_Integration (Windows PowerShell).

.DESCRIPTION
  Run from anywhere. Paths are relative to the repository root.

  Usage:
    .\scripts\local-dev.ps1 help
    .\scripts\local-dev.ps1 install
    .\scripts\local-dev.ps1 env
    .\scripts\local-dev.ps1 setup-db
    .\scripts\local-dev.ps1 api
    .\scripts\local-dev.ps1 web
    .\scripts\local-dev.ps1 worker
    .\scripts\local-dev.ps1 commands

  Prerequisites (install manually once): Git, Python 3.12+, uv, Node 22+, pnpm 9.15.4,
  PostgreSQL 16+pgvector, Redis 7+, MinIO, Mailpit. See docs/LOCAL_SETUP.md.

  Before setup-db: start PostgreSQL, Redis, MinIO (bucket: sales-agent), Mailpit.
#>
param(
    [Parameter(Position = 0)]
    [ValidateSet(
        'help',
        'install',
        'env',
        'migrate',
        'seed',
        'setup-db',
        'api',
        'web',
        'worker',
        'commands'
    )]
    [string]$Action = 'help',

    [string]$AdminEmail = 'admin@localhost',
    [string]$AdminPassword = 'ChangeMeNow123!'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path $PSScriptRoot -Parent

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

function Install-Packages {
    Write-Title 'Install Python + Node packages (order: ai-platform -> backend -> frontend)'
    Assert-Dir $Paths.AiPlatform 'ai-platform'
    Assert-Dir $Paths.Backend 'backend'
    Assert-Dir $Paths.Frontend 'frontend'

    Write-Host "Folder: $($Paths.AiPlatform)" -ForegroundColor DarkGray
    Invoke-InDir $Paths.AiPlatform { uv sync }

    Write-Host "Folder: $($Paths.Backend)" -ForegroundColor DarkGray
    Invoke-InDir $Paths.Backend { uv sync }

    Write-Host "Folder: $($Paths.Frontend)" -ForegroundColor DarkGray
    Invoke-InDir $Paths.Frontend {
        corepack enable | Out-Null
        corepack prepare pnpm@9.15.4 --activate | Out-Null
        pnpm install
    }

    Write-Host 'Packages installed.' -ForegroundColor Green
}

function Copy-EnvFiles {
    Write-Title 'Copy environment templates (skip if file already exists)'
    $backendEnv = Join-Path $Paths.Backend '.env'
    $backendExample = Join-Path $Paths.Backend '.env.example'
    $webEnv = Join-Path $Paths.WebApp '.env.local'
    $webExample = Join-Path $Paths.WebApp '.env.example'

    if (-not (Test-Path -LiteralPath $backendEnv)) {
        Copy-Item -LiteralPath $backendExample -Destination $backendEnv
        Write-Host "Created backend\.env"
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
}

function Run-Migrate {
    Write-Title 'Database migrations (Alembic)'
    Write-Host "Folder: $($Paths.Backend)" -ForegroundColor DarkGray
    Invoke-InDir $Paths.Backend { uv run alembic upgrade head }
    Write-Host 'Migrations applied.' -ForegroundColor Green
}

function Run-Seed {
    Write-Title 'Platform seed + super admin'
    Write-Host "Folder: $($Paths.Backend)" -ForegroundColor DarkGray
    Invoke-InDir $Paths.Backend {
        uv run python -m app.main.cli seed
        uv run python -m app.main.cli seed-super-admin --email $AdminEmail --password $AdminPassword
    }
    Write-Host "Seed complete. Super admin: $AdminEmail" -ForegroundColor Green
}

function Start-Api {
    Write-Title 'Backend API (blocks this terminal)'
    Write-Host 'OpenAPI: http://localhost:8000/api/v1/docs' -ForegroundColor DarkGray
    Write-Host "Folder: $($Paths.Backend)" -ForegroundColor DarkGray
    Invoke-InDir $Paths.Backend {
        uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src
    }
}

function Start-Web {
    Write-Title 'Frontend web (blocks this terminal)'
    Write-Host 'App: http://localhost:3000' -ForegroundColor DarkGray
    Write-Host "Folder: $($Paths.WebApp)" -ForegroundColor DarkGray
    Invoke-InDir $Paths.WebApp { pnpm dev }
}

function Start-Worker {
    Write-Title 'ARQ worker (optional, blocks this terminal)'
    Write-Host "Folder: $($Paths.Backend)" -ForegroundColor DarkGray
    Invoke-InDir $Paths.Backend {
        uv run arq app.workers.arq_settings.WorkerSettings
    }
}

function Show-Commands {
    Write-Title 'All commands by folder (copy/paste)'
    @"

REPO ROOT: $RepoRoot

--- One-time: install packages ---
  cd $RepoRoot\ai-platform
  uv sync

  cd $RepoRoot\backend
  uv sync

  cd $RepoRoot\frontend
  corepack enable
  corepack prepare pnpm@9.15.4 --activate
  pnpm install

--- One-time: env files (or: .\scripts\local-dev.ps1 env) ---
  Copy-Item $RepoRoot\backend\.env.example $RepoRoot\backend\.env
  Copy-Item $RepoRoot\frontend\apps\web\.env.example $RepoRoot\frontend\apps\web\.env.local

--- PostgreSQL (psql superuser): fresh DB ---
  DROP DATABASE IF EXISTS sales_agent;
  DROP USER IF EXISTS sales_agent;
  CREATE USER sales_agent WITH PASSWORD 'sales_agent';
  CREATE DATABASE sales_agent OWNER sales_agent;
  \c sales_agent
  CREATE EXTENSION IF NOT EXISTS vector;
  CREATE EXTENSION IF NOT EXISTS pg_trgm;
  CREATE EXTENSION IF NOT EXISTS citext;
  CREATE EXTENSION IF NOT EXISTS pgcrypto;

  Connection: postgresql+asyncpg://sales_agent:sales_agent@localhost:5432/sales_agent

--- Start infra (separate terminals, install binaries first) ---
  Redis/Memurai -> redis://localhost:6379/0
  minio server C:\minio-data --console-address ":9001"   # bucket: sales-agent
  mailpit                                                 # SMTP :1025, UI :8025

--- Database migrate + seed (or: .\scripts\local-dev.ps1 setup-db) ---
  cd $RepoRoot\backend
  uv run alembic upgrade head
  uv run python -m app.main.cli seed
  uv run python -m app.main.cli seed-super-admin --email admin@localhost --password "ChangeMeNow123!"

--- Run backend (or: .\scripts\local-dev.ps1 api) ---
  cd $RepoRoot\backend
  uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src

--- Run frontend (or: .\scripts\local-dev.ps1 web) ---
  cd $RepoRoot\frontend\apps\web
  pnpm dev

--- Optional worker (or: .\scripts\local-dev.ps1 worker) ---
  cd $RepoRoot\backend
  uv run arq app.workers.arq_settings.WorkerSettings

--- Fresh tenant (after login) ---
  Web: http://localhost:3000/en/login -> seller dashboard -> create workspace
  API: POST http://localhost:8000/api/v1/tenants (authenticated)

--- AI (no separate server today) ---
  backend\.env: AI_PLATFORM_MODE=in_process
  Package: installed via ai-platform\ uv sync

--- Regenerate OpenAPI client after API changes ---
  cd $RepoRoot\frontend
  pnpm gen:api

"@ | Write-Host
}

function Show-Help {
    Show-Commands
    Write-Host @'

Script shortcuts (from repo root):
  .\scripts\local-dev.ps1 install     # uv sync + pnpm install
  .\scripts\local-dev.ps1 env         # copy .env templates
  .\scripts\local-dev.ps1 migrate     # alembic upgrade head
  .\scripts\local-dev.ps1 seed        # seed + super admin
  .\scripts\local-dev.ps1 setup-db    # migrate then seed
  .\scripts\local-dev.ps1 api         # run FastAPI (terminal 1)
  .\scripts\local-dev.ps1 web         # run Next.js (terminal 2)
  .\scripts\local-dev.ps1 worker      # run ARQ worker (optional)
  .\scripts\local-dev.ps1 commands    # print command reference only

Full guide: docs\LOCAL_SETUP.md
'@ -ForegroundColor Yellow
}

switch ($Action) {
    'help' { Show-Help }
    'commands' { Show-Commands }
    'install' { Install-Packages }
    'env' { Copy-EnvFiles }
    'migrate' { Run-Migrate }
    'seed' { Run-Seed }
    'setup-db' {
        Run-Migrate
        Run-Seed
    }
    'api' { Start-Api }
    'web' { Start-Web }
    'worker' { Start-Worker }
}
