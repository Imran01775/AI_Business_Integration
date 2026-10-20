#Requires -Version 5.1
<#
.SYNOPSIS
  Beginner setup for a new Windows PC — backend, database, AI package, frontend.

.DESCRIPTION
  Open PowerShell, go to the project folder, then run:

    cd C:\Users\u1071826\Documents\Projects\AI_Business_Integration
    .\scripts\setup-new-pc.ps1

  This opens a simple menu. You can also run one step:

    .\scripts\setup-new-pc.ps1 check
    .\scripts\setup-new-pc.ps1 step-packages
    .\scripts\setup-new-pc.ps1 step-env
    .\scripts\setup-new-pc.ps1 step-docker
    .\scripts\setup-new-pc.ps1 step-database
    .\scripts\setup-new-pc.ps1 step-migrate
    .\scripts\setup-new-pc.ps1 run-backend
    .\scripts\setup-new-pc.ps1 run-frontend
    .\scripts\setup-new-pc.ps1 cheat-sheet

  Stack layout:
    - PostgreSQL  -> installed on Windows (NOT in Docker)
    - Redis/MinIO/Mailpit -> Docker (docker\compose.deps.yaml)
    - Backend API -> runs on your PC (Python/uv)
    - Frontend    -> runs on your PC (Node/pnpm)
    - AI          -> Python package ai-platform (no extra server; in_process mode)

  Need help? docs\LOCAL_SETUP.md
#>
param(
    [Parameter(Position = 0)]
    [ValidateSet(
        'menu',
        'check',
        'step-packages',
        'step-env',
        'step-docker',
        'step-database',
        'step-migrate',
        'run-backend',
        'run-frontend',
        'run-worker',
        'cheat-sheet',
        'help'
    )]
    [string]$Action = 'menu',

    [string]$AdminEmail = 'admin@localhost',
    [string]$AdminPassword = 'ChangeMeNow123!'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path $PSScriptRoot -Parent
$ComposeFile = Join-Path $RepoRoot 'docker\compose.deps.yaml'
$PostgresSql = Join-Path $RepoRoot 'docker\postgres-init.sql'

$Paths = @{
    Root       = $RepoRoot
    AiPlatform = Join-Path $RepoRoot 'ai-platform'
    Backend    = Join-Path $RepoRoot 'backend'
    Frontend   = Join-Path $RepoRoot 'frontend'
    WebApp     = Join-Path $RepoRoot 'frontend\apps\web'
}

function Write-Step([int]$Number, [string]$Title) {
    Write-Host ''
    Write-Host "----- Step $Number : $Title -----" -ForegroundColor Cyan
}

function Write-Ok([string]$Message) { Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Warn([string]$Message) { Write-Host "[!] $Message" -ForegroundColor Yellow }
function Write-Fail([string]$Message) { Write-Host "[X] $Message" -ForegroundColor Red }

function Invoke-InDir {
    param([string]$Directory, [scriptblock]$Script)
    Push-Location -LiteralPath $Directory
    try { & $Script }
    finally { Pop-Location }
}

function Test-CommandExists([string]$Name) {
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Run-CheckTools {
    Write-Step 0 'Check required tools on this PC'
    $allOk = $true

    foreach ($tool in @(
            @{ Name = 'git'; Hint = 'https://git-scm.com/download/win' },
            @{ Name = 'uv'; Hint = 'pip install uv  OR  https://docs.astral.sh/uv/' },
            @{ Name = 'node'; Hint = 'https://nodejs.org/ (v22+)' },
            @{ Name = 'docker'; Hint = 'Docker Desktop https://www.docker.com/products/docker-desktop/' }
        )) {
        if (Test-CommandExists $tool.Name) {
            Write-Ok "$($tool.Name) is installed"
        }
        else {
            Write-Fail "$($tool.Name) not found. Install: $($tool.Hint)"
            $allOk = $false
        }
    }

    if (Test-CommandExists 'pnpm') {
        Write-Ok 'pnpm is installed'
    }
    elseif (Test-CommandExists 'corepack') {
        Write-Warn 'pnpm not on PATH yet — step-packages will run: corepack enable'
    }
    else {
        Write-Fail 'Need Node.js (includes corepack) for frontend'
        $allOk = $false
    }

    if (Test-CommandExists 'psql') {
        Write-Ok 'psql found (can run database step from command line)'
    }
    else {
        Write-Warn 'psql not on PATH — use pgAdmin to run docker\postgres-init.sql'
    }

    $pgService = Get-Service -Name 'postgresql*' -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq 'Running' }
    if ($pgService) {
        Write-Ok "PostgreSQL service running: $($pgService.Name)"
    }
    else {
        Write-Warn 'PostgreSQL Windows service not detected — install PG 16 + pgvector and start the service'
    }

    if (-not $allOk) {
        Write-Warn 'Fix missing tools above, then run this check again.'
    }
    else {
        Write-Ok 'Core tools look good. Continue with the menu steps 1-6.'
    }
}

function Run-StepPackages {
    Write-Step 1 'Install project packages (AI platform, backend, frontend)'
    Write-Host @'
Order matters:
  1) ai-platform  (AI library used by backend)
  2) backend      (API)
  3) frontend     (website)
'@ -ForegroundColor DarkGray

    Write-Host 'Running: cd ai-platform && uv sync' -ForegroundColor White
    Invoke-InDir $Paths.AiPlatform { uv sync }

    Write-Host 'Running: cd backend && uv sync' -ForegroundColor White
    Invoke-InDir $Paths.Backend { uv sync }

    Write-Host 'Running: cd frontend && pnpm install' -ForegroundColor White
    Invoke-InDir $Paths.Frontend {
        corepack enable | Out-Null
        corepack prepare pnpm@9.15.4 --activate | Out-Null
        pnpm install
    }

    Write-Ok 'Packages installed.'
    Write-Host 'AI: no separate install — ai-platform folder is linked into backend.' -ForegroundColor DarkGray
}

function Run-StepEnv {
    Write-Step 2 'Create configuration files (.env)'
    $backendEnv = Join-Path $Paths.Backend '.env'
    $webEnv = Join-Path $Paths.WebApp '.env.local'

    if (-not (Test-Path $backendEnv)) {
        Copy-Item (Join-Path $Paths.Backend '.env.example') $backendEnv
        Write-Ok 'Created backend\.env'
    }
    else { Write-Warn 'backend\.env already exists (kept as-is)' }

    if (-not (Test-Path $webEnv)) {
        Copy-Item (Join-Path $Paths.WebApp '.env.example') $webEnv
        Write-Ok 'Created frontend\apps\web\.env.local'
    }
    else { Write-Warn 'frontend\apps\web\.env.local already exists (kept as-is)' }

    Write-Host @'

Important settings (usually default is fine):
  backend\.env
    DATABASE_URL  -> local PostgreSQL localhost:5432
    REDIS_URL     -> redis://localhost:6379/0  (Docker)
    S3_*          -> MinIO on localhost:9000   (Docker)
    SMTP_*        -> Mailpit localhost:1025    (Docker)
    AI_PLATFORM_MODE=in_process   (AI runs inside backend — no extra command)
'@ -ForegroundColor DarkGray
}

function Run-StepDocker {
    Write-Step 3 'Start supporting services in Docker (Redis, MinIO, Mailpit)'
    if (-not (Test-Path $ComposeFile)) {
        throw "Missing $ComposeFile"
    }
    if (-not (Test-CommandExists 'docker')) {
        throw 'Install Docker Desktop first, then run this step again.'
    }

    Write-Host "Command: docker compose -f docker\compose.deps.yaml up -d" -ForegroundColor White
    & docker compose -f $ComposeFile up -d
    if ($LASTEXITCODE -ne 0) { throw 'docker compose failed' }

    Write-Ok 'Docker services started.'
    Write-Host '  Redis    localhost:6379' -ForegroundColor DarkGray
    Write-Host '  MinIO    http://localhost:9000  (console :9001, user/pass minioadmin)' -ForegroundColor DarkGray
    Write-Host '  Mailpit  http://localhost:8025  (test emails)' -ForegroundColor DarkGray
}

function Run-StepDatabase {
    Write-Step 4 'Create PostgreSQL database on THIS PC (not Docker)'
    Write-Host "SQL script: $PostgresSql" -ForegroundColor White
    Write-Host @'

You only do this once (or when you want a completely fresh database).

Option A — Command line (if psql is installed):
  psql -U postgres -f docker\postgres-init.sql

Option B — pgAdmin:
  1) Connect as postgres superuser
  2) Open docker\postgres-init.sql
  3) Execute the script

This creates:
  database: sales_agent
  user:     sales_agent / password sales_agent
  extensions: vector, pg_trgm, citext, pgcrypto

'@ -ForegroundColor DarkGray

    if (Test-CommandExists 'psql') {
        $answer = Read-Host 'Run psql now as user postgres? (y/N)'
        if ($answer -match '^[yY]') {
            & psql -U postgres -f $PostgresSql
            if ($LASTEXITCODE -eq 0) { Write-Ok 'Database created.' }
            else { Write-Warn 'psql failed — use pgAdmin or fix PostgreSQL install.' }
        }
    }
    else {
        Write-Warn 'Install PostgreSQL 16 + pgvector, then run the SQL file manually.'
    }
}

function Run-StepMigrate {
    Write-Step 5 'Apply database tables + seed data + admin user'
    Write-Host 'Folder: backend' -ForegroundColor DarkGray
    Write-Host @'
Commands:
  uv run alembic upgrade head
  uv run python -m app.main.cli seed
  uv run python -m app.main.cli seed-super-admin ...
'@ -ForegroundColor White

    $email = $AdminEmail
    $password = $AdminPassword
    Invoke-InDir $Paths.Backend {
        uv run alembic upgrade head
        uv run python -m app.main.cli seed
        uv run python -m app.main.cli seed-super-admin --email $email --password $password
    }

    Write-Ok 'Database ready.'
    Write-Host "  Super admin login: $AdminEmail / $AdminPassword" -ForegroundColor Green
    Write-Host '  Then open http://localhost:3000/en/login and create a workspace (new tenant).' -ForegroundColor Green
}

function Run-Backend {
    Write-Step 6 'Run BACKEND (keep this window open)'
    Write-Host @'
Use a DEDICATED PowerShell window. Stop with Ctrl+C.

Folder:
  cd backend

Command:
  uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src

URLs:
  API docs: http://localhost:8000/api/v1/docs
'@ -ForegroundColor DarkGray

    $start = Read-Host 'Start backend now in this window? (y/N)'
    if ($start -match '^[yY]') {
        Invoke-InDir $Paths.Backend {
            uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src
        }
    }
}

function Run-Frontend {
    Write-Step 7 'Run FRONTEND (second PowerShell window)'
    Write-Host @'
Open a NEW PowerShell window. Stop with Ctrl+C.

Folder:
  cd frontend\apps\web

Command:
  pnpm dev

URL:
  http://localhost:3000
'@ -ForegroundColor DarkGray

    $start = Read-Host 'Start frontend now in this window? (y/N)'
    if ($start -match '^[yY]') {
        Invoke-InDir $Paths.WebApp { pnpm dev }
    }
}

function Run-Worker {
    Write-Host @'
OPTIONAL — background jobs (third window):

Folder:
  cd backend

Command:
  uv run arq app.workers.arq_settings.WorkerSettings
'@ -ForegroundColor DarkGray

    $start = Read-Host 'Start worker now? (y/N)'
    if ($start -match '^[yY]') {
        Invoke-InDir $Paths.Backend {
            uv run arq app.workers.arq_settings.WorkerSettings
        }
    }
}

function Show-CheatSheet {
    Write-Host ''
    Write-Host '========== DAILY CHEAT SHEET (after first setup) ==========' -ForegroundColor Cyan
    Write-Host @"

Project folder:
  cd $RepoRoot

1) Start Docker helpers (each work day):
   docker compose -f docker\compose.deps.yaml up -d

2) Start BACKEND (terminal 1):
   cd backend
   uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src

3) Start FRONTEND (terminal 2):
   cd frontend\apps\web
   pnpm dev

4) AI:
   No extra terminal. Backend uses ai-platform (AI_PLATFORM_MODE=in_process).

5) Fresh database reset:
   psql -U postgres -f docker\postgres-init.sql
   cd backend
   uv run alembic upgrade head
   uv run python -m app.main.cli seed
   uv run python -m app.main.cli seed-super-admin --email admin@localhost --password "ChangeMeNow123!"

6) Stop Docker when done:
   docker compose -f docker\compose.deps.yaml down

Login: admin@localhost / ChangeMeNow123!
Mailpit (registration emails): http://localhost:8025

"@ -ForegroundColor White
}

function Show-Menu {
    Show-CheatSheet
    Write-Host '========== FIRST-TIME SETUP MENU ==========' -ForegroundColor Cyan
    Write-Host '  c  Check tools'
    Write-Host '  1  Install packages (ai-platform, backend, frontend)'
    Write-Host '  2  Create .env files'
    Write-Host '  3  Start Docker (Redis, MinIO, Mailpit)'
    Write-Host '  4  Create PostgreSQL database (local)'
    Write-Host '  5  Migrations + seed + admin user'
    Write-Host '  6  Run backend (API)'
    Write-Host '  7  Run frontend (website)'
    Write-Host '  w  Run worker (optional)'
    Write-Host '  s  Show cheat sheet again'
    Write-Host '  q  Quit'
    Write-Host ''

    while ($true) {
        $choice = Read-Host 'Choose step (c,1-7,w,s,q)'
        switch -Regex ($choice) {
            '^[cC]$' { Run-CheckTools }
            '^1$' { Run-StepPackages }
            '^2$' { Run-StepEnv }
            '^3$' { Run-StepDocker }
            '^4$' { Run-StepDatabase }
            '^5$' { Run-StepMigrate }
            '^6$' { Run-Backend }
            '^7$' { Run-Frontend }
            '^[wW]$' { Run-Worker }
            '^[sS]$' { Show-CheatSheet }
            '^[qQ]$' { return }
            default { Write-Warn 'Unknown choice.' }
        }
    }
}

switch ($Action) {
    'menu' { Show-Menu }
    'help' { Show-CheatSheet }
    'cheat-sheet' { Show-CheatSheet }
    'check' { Run-CheckTools }
    'step-packages' { Run-StepPackages }
    'step-env' { Run-StepEnv }
    'step-docker' { Run-StepDocker }
    'step-database' { Run-StepDatabase }
    'step-migrate' { Run-StepMigrate }
    'run-backend' { Run-Backend }
    'run-frontend' { Run-Frontend }
    'run-worker' { Run-Worker }
}
