"""platform: core database schema and RLS (Phase 02)

Revision ID: 20261013_0001
Revises:
Create Date: 2026-10-13

Module: platform
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261013_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RLS_TENANT_TABLES = (
    "setting_values",
    "message_templates",
    "secrets",
    "audit_log",
    "error_events",
    "job_failures",
    "idempotency_keys",
    "sync_connections",
    "sync_jobs",
)


def _enable_tenant_rls_sql() -> str:
    return """
    CREATE OR REPLACE FUNCTION enable_tenant_rls(target_table regclass)
    RETURNS void
    LANGUAGE plpgsql
    AS $$
    BEGIN
        EXECUTE format('ALTER TABLE %s ENABLE ROW LEVEL SECURITY', target_table);
        EXECUTE format('ALTER TABLE %s FORCE ROW LEVEL SECURITY', target_table);
        EXECUTE format(
            'CREATE POLICY tenant_isolation ON %s
             USING (
               tenant_id IS NULL
               OR tenant_id = NULLIF(current_setting(''app.tenant_id'', true), '''')::uuid
             )',
            target_table
        );
    END;
    $$;
    """


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.execute(_enable_tenant_rls_sql())

    op.execute(
        """
        DO $$
        BEGIN
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_owner') THEN
                    CREATE ROLE app_owner NOLOGIN;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_rw') THEN
                    CREATE ROLE app_rw LOGIN PASSWORD 'app_rw_dev_change_me' NOBYPASSRLS;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_platform') THEN
                    CREATE ROLE app_platform LOGIN PASSWORD 'app_platform_dev_change_me' BYPASSRLS;
                END IF;
            EXCEPTION WHEN insufficient_privilege THEN
                RAISE NOTICE
                    'Skipping CREATE ROLE (need CREATEROLE). Run docker/postgres-init.sql as a superuser.';
            END;
        END
        $$;
        """
    )

    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("display_name", sa.String(256), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "setting_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(128), nullable=False, unique=True),
        sa.Column("chain", sa.String(16), nullable=False),
        sa.Column("value_type", sa.String(32), nullable=False),
        sa.Column("default_value", postgresql.JSONB, nullable=False),
        sa.Column("schema", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("overridable_at", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("bounded_by", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("edit_permission", sa.String(128), nullable=False),
        sa.Column("entitlement", sa.String(128), nullable=True),
        sa.Column("is_secret", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "setting_values",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scope_layer", sa.String(32), nullable=False),
        sa.Column("scope_id", sa.String(64), nullable=True),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value", postgresql.JSONB, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "scope_layer",
            "scope_id",
            "key",
            name="uq_setting_values_scope_key",
        ),
    )
    op.create_index("ix_setting_values_tenant_id", "setting_values", ["tenant_id"])
    op.create_index("ix_setting_values_key", "setting_values", ["key"])

    op.create_table(
        "setting_values_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scope_layer", sa.String(32), nullable=False),
        sa.Column("scope_id", sa.String(64), nullable=True),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value", postgresql.JSONB, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("changed_by", sa.String(64), nullable=True),
    )
    op.create_index("ix_setting_values_history_tenant_id", "setting_values_history", ["tenant_id"])

    op.create_table(
        "message_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("locale", sa.String(8), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("variables", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("tenant_id", "key", "locale", name="uq_message_templates_tenant_key_locale"),
    )
    op.create_index("ix_message_templates_tenant_id", "message_templates", ["tenant_id"])

    op.create_table(
        "message_templates_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("locale", sa.String(8), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("variables", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "secrets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("scope_id", sa.String(64), nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("key_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("tenant_id", "scope_type", "scope_id", "key", name="uq_secrets_scope_key"),
    )
    op.create_index("ix_secrets_tenant_id", "secrets", ["tenant_id"])

    op.create_table(
        "outbox_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("topic", sa.String(128), nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_outbox_events_tenant_id", "outbox_events", ["tenant_id"])
    op.create_index("ix_outbox_events_status", "outbox_events", ["status"])

    op.create_table(
        "processed_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("consumer_name", sa.String(128), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("consumer_name", "event_id", name="uq_processed_events_consumer_event"),
    )

    op.create_table(
        "idempotency_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", sa.String(256), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=True),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column("response_body", postgresql.JSONB, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_idempotency_keys_tenant_key"),
    )
    op.create_index("ix_idempotency_keys_tenant_id", "idempotency_keys", ["tenant_id"])

    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_type", sa.String(32), nullable=True),
        sa.Column("actor_id", sa.String(64), nullable=True),
        sa.Column("impersonator_id", sa.String(64), nullable=True),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("before", postgresql.JSONB, nullable=True),
        sa.Column("after", postgresql.JSONB, nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("trace_id", sa.String(64), nullable=False),
    )
    op.create_index("ix_audit_log_tenant_id", "audit_log", ["tenant_id"])
    op.create_index("ix_audit_log_occurred_at", "audit_log", ["occurred_at"])

    op.create_table(
        "error_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("module", sa.String(64), nullable=False),
        sa.Column("code", sa.String(128), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False, server_default="error"),
        sa.Column("source_type", sa.String(64), nullable=True),
        sa.Column("source_id", sa.String(64), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("context", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("payload_ref", sa.String(512), nullable=True),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.String(64), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
    )
    op.create_index("ix_error_events_tenant_id", "error_events", ["tenant_id"])

    op.create_table(
        "job_failures",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("job_name", sa.String(128), nullable=False),
        sa.Column("queue", sa.String(64), nullable=False),
        sa.Column("payload_ref", sa.String(512), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error_code", sa.String(128), nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_job_failures_tenant_id", "job_failures", ["tenant_id"])

    op.create_table(
        "feature_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_feature_flags_tenant_id", "feature_flags", ["tenant_id"])

    op.create_table(
        "sync_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="inactive"),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_sync_connections_tenant_id", "sync_connections", ["tenant_id"])

    op.create_table(
        "sync_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_sync_jobs_tenant_id", "sync_jobs", ["tenant_id"])

    for table in RLS_TENANT_TABLES:
        op.execute(sa.text(f"SELECT enable_tenant_rls('{table}'::regclass)"))

    op.execute(
        """
        DO $grant$
        DECLARE dbname text := current_database();
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_rw')
               OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_platform') THEN
                RAISE NOTICE 'Skipping GRANTs to app_rw/app_platform; roles not present.';
                RETURN;
            END IF;
            EXECUTE format('GRANT CONNECT ON DATABASE %I TO app_rw, app_platform', dbname);
            GRANT USAGE ON SCHEMA public TO app_rw, app_platform;
            GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_rw, app_platform;
            GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_rw, app_platform;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public
                GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_rw, app_platform;
        END
        $grant$;
        """
    )


def downgrade() -> None:
    for table in reversed(RLS_TENANT_TABLES):
        op.execute(sa.text(f"DROP POLICY IF EXISTS tenant_isolation ON {table}"))
        op.execute(sa.text(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY"))

    op.drop_table("sync_jobs")
    op.drop_table("sync_connections")
    op.drop_table("feature_flags")
    op.drop_table("job_failures")
    op.drop_table("error_events")
    op.drop_table("audit_log")
    op.drop_table("idempotency_keys")
    op.drop_table("processed_events")
    op.drop_table("outbox_events")
    op.drop_table("secrets")
    op.drop_table("message_templates_history")
    op.drop_table("message_templates")
    op.drop_table("setting_values_history")
    op.drop_table("setting_values")
    op.drop_table("setting_definitions")
    op.drop_table("tenants")

    op.execute("DROP FUNCTION IF EXISTS enable_tenant_rls(regclass)")
    op.execute("DROP ROLE IF EXISTS app_platform")
    op.execute("DROP ROLE IF EXISTS app_rw")
    op.execute("DROP ROLE IF EXISTS app_owner")
