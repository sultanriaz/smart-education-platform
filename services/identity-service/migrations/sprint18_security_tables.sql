-- Reference SQL for the Sprint 18 Identity migration.
-- Codex must convert this into the next real Alembic revision using the current
-- Identity migration head as down_revision.

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    token_digest VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_user_expires
    ON password_reset_tokens (user_id, expires_at);

CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    token_digest VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_email_verification_tokens_user_expires
    ON email_verification_tokens (user_id, expires_at);

-- Optional cleanup indexes if the real PostgreSQL workload shows they help:
CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_expires_at
    ON password_reset_tokens (expires_at);

CREATE INDEX IF NOT EXISTS ix_email_verification_tokens_expires_at
    ON email_verification_tokens (expires_at);
