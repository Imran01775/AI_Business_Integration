-- Run on LOCAL PostgreSQL 16+ (Windows installer or WSL), as superuser (e.g. postgres).
-- Not used by Docker — database stays on the host; backend uses localhost:5432.

DROP DATABASE IF EXISTS sales_agent;
DROP USER IF EXISTS sales_agent;

CREATE USER sales_agent WITH PASSWORD 'sales_agent';
CREATE DATABASE sales_agent OWNER sales_agent;

-- Alembic creates these if the connecting user has CREATEROLE; create them here as superuser
-- so `uv run alembic upgrade head` works as sales_agent on a local Windows install.
CREATE ROLE app_owner NOLOGIN;
CREATE ROLE app_rw LOGIN PASSWORD 'app_rw_dev_change_me' NOBYPASSRLS;
CREATE ROLE app_platform LOGIN PASSWORD 'app_platform_dev_change_me' BYPASSRLS;

\c sales_agent

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

GRANT CONNECT ON DATABASE sales_agent TO app_rw, app_platform;
GRANT USAGE ON SCHEMA public TO app_rw, app_platform;

-- backend/.env:
-- DATABASE_URL=postgresql+asyncpg://sales_agent:sales_agent@localhost:5432/sales_agent
